"""
Tests pour l'endpoint GET /api/players/{player_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/players/test_get_player.py -v
"""
import pytest
from uuid import uuid4

from schemas import GameCreate, LobbyCreate
from schemas.player import PlayerCreate
from repositories import GameRepository, LobbyRepository, PlayerRepository
from tests.api.helpers import create_user_and_get_token, get_auth_headers
from tests.api.players.helpers import get_player_url


# 200 - Success
@pytest.mark.asyncio
async def test_get_player_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'un joueur avec succès."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
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
        get_player_url(player.id),
        headers=get_auth_headers(token1)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(player.id)
    assert data["user_id"] == str(user2.id)


# 404 - Not Found
@pytest.mark.asyncio
async def test_get_player_not_found(client, auth_service):
    """Test récupération d'un joueur inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        get_player_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_get_player_invalid_uuid(client, auth_service):
    """Test récupération d'un joueur avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_player_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_get_player_unauthorized(client):
    """Test récupération d'un joueur sans authentification."""
    fake_id = uuid4()
    response = await client.get(
        get_player_url(fake_id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

