"""
Tests pour les endpoints /api/lobbies.

shortcut : uv run pytest tests/api/test_lobbies.py -v
"""
import pytest
from uuid import uuid4


from schemas import GameCreate, LobbyCreate
from models import LobbyStatus
from repositories import GameRepository, LobbyRepository
from tests.api.helpers import create_user_and_get_token, get_auth_headers


@pytest.mark.asyncio
async def test_create_lobby_success(client, auth_service, db_session, initialized_game_types):
    """Test création d'un lobby avec succès."""
    user, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Créer un lobby
    response = await client.post(
        "/api/lobbies",
        json={
            "name": "Test Lobby",
            "game_id": str(game.id),
            "min_players": 2,
            "max_players": 10
        },
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Lobby"
    assert data["host_id"] == str(user.id)
    assert data["status"] == LobbyStatus.WAITING.value
    assert "code" in data


@pytest.mark.asyncio
async def test_create_lobby_game_not_found(client, auth_service):
    """Test création d'un lobby avec un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_game_id = uuid4()
    response = await client.post(
        "/api/lobbies",
        json={
            "name": "Test Lobby",
            "game_id": str(fake_game_id),
            "min_players": 2,
            "max_players": 10
        },
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "game" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_lobby_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'un lobby avec succès."""
    user, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game_repo = GameRepository(db_session)
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
        user.id
    )
    
    # Récupérer le lobby
    response = await client.get(
        f"/api/lobbies/{lobby.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(lobby.id)
    assert data["game"]["id"] == str(game.id)


@pytest.mark.asyncio
async def test_get_lobby_not_found(client, auth_service):
    """Test récupération d'un lobby inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        f"/api/lobbies/{fake_id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_lobby_by_code_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'un lobby par code avec succès."""
    user, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game_repo = GameRepository(db_session)
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
        user.id
    )
    
    # Récupérer le lobby par code
    response = await client.get(
        f"/api/lobbies/code/{lobby.code}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(lobby.id)
    assert data["code"] == lobby.code


@pytest.mark.asyncio
async def test_get_lobby_by_code_not_found(client, auth_service):
    """Test récupération d'un lobby par code inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        "/api/lobbies/code/INVALID",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_lobbies_success(client, auth_service, db_session, initialized_game_types):
    """Test liste des lobbies avec succès."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    lobby_repo = LobbyRepository(db_session)
    lobby1 = await lobby_repo.create_lobby(
        LobbyCreate(name="Lobby 1", game_id=game.id, min_players=2, max_players=10),
        user1.id
    )
    lobby2 = await lobby_repo.create_lobby(
        LobbyCreate(name="Lobby 2", game_id=game.id, min_players=2, max_players=10),
        user2.id
    )
    
    # Lister les lobbies publics
    response = await client.get(
        "/api/lobbies",
        headers=get_auth_headers(token1)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    lobby_ids = [l["id"] for l in data]
    assert str(lobby1.id) in lobby_ids
    assert str(lobby2.id) in lobby_ids


@pytest.mark.asyncio
async def test_delete_lobby_as_host(client, auth_service, db_session, initialized_game_types):
    """Test suppression d'un lobby par le host."""
    user, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game_repo = GameRepository(db_session)
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
        user.id
    )
    
    # Supprimer le lobby
    response = await client.delete(
        f"/api/lobbies/{lobby.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 204
    
    # Vérifier que le lobby n'existe plus
    response = await client.get(
        f"/api/lobbies/{lobby.id}",
        headers=get_auth_headers(token)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_lobby_not_host(client, auth_service, db_session, initialized_game_types):
    """Test suppression d'un lobby par un joueur qui n'est pas le host."""
    
    user, token = await create_user_and_get_token(client, auth_service)
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game_repo = GameRepository(db_session)
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
        user.id
    )
    # Tenter de supprimer le lobby
    response = await client.delete(
        f"/api/lobbies/{lobby.id}",
        headers=get_auth_headers(token2)
    )
    assert response.status_code == 403
    assert "host" in response.json()["detail"].lower()
