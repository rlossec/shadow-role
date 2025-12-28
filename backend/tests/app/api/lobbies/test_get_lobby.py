"""
Tests pour l'endpoint GET /api/lobbies/{lobby_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/lobbies/test_get_lobby.py -v
"""
import pytest
from uuid import uuid4

from app.models.game import GameTypeEnum
from app.schemas import GameCreate, LobbyCreate
from app.repositories import GameRepository, LobbyRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.lobbies.helpers import get_lobby_url


# 200 - Success
@pytest.mark.asyncio
async def test_get_lobby_success(client, auth_service, db_session):
    """Test récupération d'un lobby avec succès."""
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
    
    # Récupérer le lobby
    response = await client.get(
        get_lobby_url(lobby.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(lobby.id)
    assert data["name"] == "Test Lobby"
    assert data["game"]["id"] == str(game.id)


# 404 - Not Found
@pytest.mark.asyncio
async def test_get_lobby_not_found(client, auth_service):
    """Test récupération d'un lobby inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        get_lobby_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "lobby" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_get_lobby_invalid_uuid(client, auth_service):
    """Test récupération d'un lobby avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_lobby_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_get_lobby_unauthorized(client, auth_service, db_session):
    """Test récupération d'un lobby sans authentification."""
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
    
    response = await client.get(
        get_lobby_url(lobby.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

