"""
Tests pour l'endpoint GET /api/players/lobby/{lobby_id}.

Pour exécuter ces tests:
    uv run pytest tests/app/api/players/test_get_lobby_players.py -v
"""
import pytest
from uuid import uuid4

from app.models import GameTypeEnum
from app.schemas import GameCreate, LobbyCreate, PlayerCreate
from app.repositories import GameRepository, LobbyRepository, PlayerRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.players.helpers import get_lobby_players_url


# 200 - Success
@pytest.mark.asyncio
async def test_get_lobby_players_success(client, auth_service, db_session):
    """Test récupération des joueurs d'un lobby avec succès."""
    user1, token1 = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    user2, token2 = await create_user_and_get_token(client, auth_service, "user2", "user2@test.com")
    
    # Créer un jeu et un lobby
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
    player1 = await player_repo.create_player(
        PlayerCreate(
            lobby_id=lobby.id,
            user_id=user1.id,
            alias="Test Player",
            color="red"
        )
    )
    player2 = await player_repo.create_player(
        PlayerCreate(
            lobby_id=lobby.id,
            user_id=user2.id,
            alias="Test Player",
            color="red"
        )
    )
    
    # Récupérer les joueurs du lobby
    response = await client.get(
        get_lobby_players_url(lobby.id),
        headers=get_auth_headers(token1)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    player_ids = [p["id"] for p in data]
    assert str(player1.id) in player_ids
    assert str(player2.id) in player_ids


# 404 - Not Found
@pytest.mark.asyncio
async def test_get_lobby_players_lobby_not_found(client, auth_service):
    """Test récupération des joueurs d'un lobby inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        get_lobby_players_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "lobby" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_get_lobby_players_invalid_uuid(client, auth_service):
    """Test récupération des joueurs avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_lobby_players_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_get_lobby_players_unauthorized(client, auth_service, db_session):
    """Test récupération des joueurs sans authentification."""
    user1, _ = await create_user_and_get_token(client, auth_service, "user1", "user1@test.com")
    
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
    
    response = await client.get(
        get_lobby_players_url(lobby.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

