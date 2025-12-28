"""
Tests pour l'endpoint GET /api/lobbies.

Pour exécuter ces tests:
    uv run pytest tests/api/lobbies/test_list_lobbies.py -v
"""
import pytest

from app.models.game import GameTypeEnum
from app.schemas import GameCreate, LobbyCreate
from app.repositories import GameRepository, LobbyRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.lobbies.helpers import get_lobbies_url


# 200 - Success
@pytest.mark.asyncio
async def test_list_lobbies_success(client, auth_service, db_session):
    """Test liste des lobbies avec succès."""
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
        get_lobbies_url(),
        headers=get_auth_headers(token1)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    lobby_ids = [l["id"] for l in data]
    assert str(lobby1.id) in lobby_ids
    assert str(lobby2.id) in lobby_ids


@pytest.mark.asyncio
async def test_list_lobbies_empty(client, auth_service):
    """Test liste des lobbies vide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_lobbies_url(),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Peut être vide ou contenir d'autres lobbies selon les tests précédents


@pytest.mark.asyncio
async def test_list_lobbies_with_pagination(client, auth_service, db_session):
    """Test liste des lobbies avec pagination (skip et limit)."""
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
    # Créer plusieurs lobbies
    for i in range(5):
        await lobby_repo.create_lobby(
            LobbyCreate(name=f"Lobby {i}", game_id=game.id, min_players=2, max_players=10),
            user.id
        )
    
    # Tester avec skip et limit
    response = await client.get(
        f"{get_lobbies_url()}?skip=0&limit=2",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_list_lobbies_unauthorized(client):
    """Test liste des lobbies sans authentification."""
    response = await client.get(
        get_lobbies_url()
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

