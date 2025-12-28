"""
Tests pour l'endpoint GET /api/players/{player_id}/mission.

Pour exécuter ces tests:
    uv run pytest tests/api/players/test_get_player_missions.py -v
"""
import pytest
from uuid import uuid4

from app.models import GameTypeEnum
from app.schemas import GameCreate, LobbyCreate, MissionCreate, PlayerCreate
from app.repositories import GameRepository, LobbyRepository, PlayerRepository, MissionRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.players.helpers import get_player_missions_url


# 200 - Success
@pytest.mark.asyncio
async def test_get_player_missions_success(client, auth_service, db_session):
    """Test récupération des missions d'un joueur avec succès."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")

    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Test Lobby", game_id=game.id, min_players=2, max_players=10),
        user1.id
    )
    
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
    
    player_repo = PlayerRepository(db_session)
    player = await player_repo.create_player(
        PlayerCreate(
            lobby_id=lobby.id,
            user_id=user2.id,
            alias="Test Player",
            color="red"
        )
    )
    
    # Récupérer les missions du joueur
    response = await client.get(
        get_player_missions_url(player.id),
        headers=get_auth_headers(token2)  # token du joueur lui-même
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_player_missions_by_host(client, auth_service, db_session):
    """Test récupération des missions d'un joueur par le host."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")

    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Test Lobby", game_id=game.id, min_players=2, max_players=10),
        user1.id  # user1 est le host
    )
    
    player_repo = PlayerRepository(db_session)
    player = await player_repo.create_player(
        PlayerCreate(
            lobby_id=lobby.id,
            user_id=user2.id,
            alias="Test Player",
            color="red"
        )
    )
    
    # Récupérer les missions du joueur par le host
    response = await client.get(
        get_player_missions_url(player.id),
        headers=get_auth_headers(token1)  # token du host
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# 404 - Not Found
@pytest.mark.asyncio
async def test_get_player_missions_player_not_found(client, auth_service):
    """Test récupération des missions d'un joueur inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        get_player_missions_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


# 403 - Forbidden (pas le joueur ni le host)
@pytest.mark.asyncio
async def test_get_player_missions_forbidden(client, auth_service, db_session):
    """Test récupération des missions d'un joueur par un utilisateur non autorisé."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    user3, token3 = await create_user_and_get_token(client, auth_service, "user3", "user3@test.com")
    
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Test Lobby", game_id=game.id, min_players=2, max_players=10),
        user1.id  # user1 est le host
    )
    
    player_repo = PlayerRepository(db_session)
    player = await player_repo.create_player(
        PlayerCreate(
            lobby_id=lobby.id,
            user_id=user2.id,
            alias="Test Player",
            color="red"
        )
    )
    
    # Tenter de récupérer avec user3 qui n'est ni le joueur ni le host
    response = await client.get(
        get_player_missions_url(player.id),
        headers=get_auth_headers(token3)  # token de user3
    )
    
    assert response.status_code == 403


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_get_player_missions_invalid_uuid(client, auth_service):
    """Test récupération des missions avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_player_missions_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_get_player_missions_unauthorized(client, auth_service, db_session):
    """Test récupération des missions sans authentification."""
    user1, _ = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, _ = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Test Lobby", game_id=game.id, min_players=2, max_players=10),
        user1.id
    )
    
    player_repo = PlayerRepository(db_session)
    player = await player_repo.create_player(
        PlayerCreate(
            lobby_id=lobby.id,
            user_id=user2.id,
            alias="Test Player",
            color="red"
        )
    )
    
    response = await client.get(
        get_player_missions_url(player.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

