"""
Tests pour l'endpoint DELETE /api/lobbies/{lobby_id}.

Pour exécuter ces tests:
    uv run pytest tests/app/api/lobbies/test_delete_lobby.py -v
"""
import pytest
from uuid import uuid4

from app.models.game import GameTypeEnum
from app.schemas import GameCreate, LobbyCreate
from app.repositories import GameRepository, LobbyRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.lobbies.helpers import get_lobby_url, get_delete_lobby_url


# 204 - Success (No Content)
@pytest.mark.asyncio
async def test_delete_lobby_as_host(client, auth_service, db_session):
    """Test suppression d'un lobby par le host."""
    user, token = await create_user_and_get_token(client, auth_service)

    
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
        user.id
    )
    
    # Supprimer le lobby
    response = await client.delete(
        get_delete_lobby_url(lobby.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 204
    assert response.content == b""  # Pas de contenu pour 204
    
    # Vérifier que le lobby n'existe plus
    response = await client.get(
        get_lobby_url(lobby.id),
        headers=get_auth_headers(token)
    )
    assert response.status_code == 404


# 404 - Not Found
@pytest.mark.asyncio
async def test_delete_lobby_not_found(client, auth_service):
    """Test suppression d'un lobby inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.delete(
        get_delete_lobby_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "lobby" in response.json()["detail"].lower()


# 403 - Forbidden (pas le host)
@pytest.mark.asyncio
async def test_delete_lobby_not_host(client, auth_service, db_session):
    """Test suppression d'un lobby par un joueur qui n'est pas le host."""
    
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
    
    # Tenter de supprimer le lobby avec user2 qui n'est pas le host
    response = await client.delete(
        get_delete_lobby_url(lobby.id),
        headers=get_auth_headers(token2)  # token de user2
    )
    
    assert response.status_code == 403
    assert "host" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_delete_lobby_invalid_uuid(client, auth_service):
    """Test suppression d'un lobby avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.delete(
        get_delete_lobby_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_delete_lobby_unauthorized(client, auth_service, db_session):
    """Test suppression d'un lobby sans authentification."""
    user, _ = await create_user_and_get_token(client, auth_service)
    
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
        user.id
    )
    
    response = await client.delete(
        get_delete_lobby_url(lobby.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

