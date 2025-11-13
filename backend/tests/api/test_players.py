"""
Tests pour les endpoints /api/players.

shortcut : uv run pytest tests/api/test_players.py -v
"""
import pytest
from uuid import uuid4

from tests.api.helpers import create_user_and_get_token, get_auth_headers

from schemas import GameCreate, LobbyCreate

from schemas.player import PlayerCreate
from repositories.game_repository import GameRepository
from repositories.lobby_repository import LobbyRepository
from repositories.player_repository import PlayerRepository
from repositories.mission_repository import MissionRepository


@pytest.mark.asyncio
async def test_get_player_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'un joueur avec succès."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Créer un lobby
    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Test Lobby", game_id=game.id, min_players=2, max_players=10),
        user1.id
    )
    
    # Créer un joueur
    player_repo = PlayerRepository(db_session)
    player = await player_repo.create_player(
        PlayerCreate(lobby_id=lobby.id),
        user2.id
    )
    
    # Récupérer le joueur
    response = await client.get(
        f"/api/players/{player.id}",
        headers=get_auth_headers(token1)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(player.id)
    assert data["user_id"] == str(user2.id)


@pytest.mark.asyncio
async def test_get_player_not_found(client, auth_service):
    """Test récupération d'un joueur inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        f"/api/players/{fake_id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_player_unauthorized(client):
    """Test récupération d'un joueur sans authentification."""
    fake_id = uuid4()
    response = await client.get(f"/api/players/{fake_id}")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_player_missions_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération des missions d'un joueur avec succès."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")

    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Test Lobby", game_id=game.id, min_players=2, max_players=10),
        user1.id
    )
    
    from schemas.mission import MissionCreate
    mission_repo = MissionRepository(db_session)
    mission1 = await mission_repo.create_mission(MissionCreate(
        title="Mission 1",
        description="Test",
        difficulty=50,
        game_id=game.id
    ))
    mission2 = await mission_repo.create_mission(MissionCreate(
        title="Mission 2",
        description="Test",
        difficulty=75,
        game_id=game.id
    ))
    
    from schemas.player import PlayerCreate
    player_repo = PlayerRepository(db_session)
    player = await player_repo.create_player(
        PlayerCreate(lobby_id=lobby.id),
        user2.id
    )
    
    # Récupérer les missions du joueur
    response = await client.get(
        f"/api/players/{player.id}/mission",
        headers=get_auth_headers(token2)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_lobby_players_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération des joueurs d'un lobby avec succès."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    
    # Créer un jeu et un lobby
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Test Lobby", game_id=game.id, min_players=2, max_players=10),
        user1.id
    )
    
    from schemas.player import PlayerCreate
    player_repo = PlayerRepository(db_session)
    player1 = await player_repo.create_player(
        PlayerCreate(lobby_id=lobby.id),
        user1.id
    )
    player2 = await player_repo.create_player(
        PlayerCreate(lobby_id=lobby.id),
        user2.id
    )
    
    # Récupérer les joueurs du lobby
    response = await client.get(
        f"/api/players/lobby/{lobby.id}",
        headers=get_auth_headers(token1)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    player_ids = [p["id"] for p in data]
    assert str(player1.id) in player_ids
    assert str(player2.id) in player_ids


@pytest.mark.asyncio
async def test_get_lobby_players_lobby_not_found(client, auth_service):
    """Test récupération des joueurs d'un lobby inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        f"/api/players/lobby/{fake_id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404

