"""
Tests pour l'endpoint PUT /api/players/{player_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/players/test_update_player.py -v
"""
import pytest
from uuid import uuid4

from app.models import GameTypeEnum
from app.schemas import GameCreate, LobbyCreate, PlayerCreate
from app.repositories import GameRepository, LobbyRepository, PlayerRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.players.helpers import get_base_player_update_payload, get_update_player_url


# 200 - Success
@pytest.mark.asyncio
async def test_update_player_success(client, auth_service, db_session):
    """Test mise à jour d'un joueur avec succès."""
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
    player = await player_repo.create_player(
        PlayerCreate(
            lobby_id=lobby.id,
            user_id=user2.id,
            alias="Test Player",
            color="red"
        )
    )
    
    # Mettre à jour le joueur (par lui-même)
    payload = get_base_player_update_payload()
    response = await client.put(
        get_update_player_url(player.id),
        json=payload,
        headers=get_auth_headers(token2)  # token du joueur lui-même
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == payload["score"]


@pytest.mark.asyncio
async def test_update_player_by_host(client, auth_service, db_session):
    """Test mise à jour d'un joueur par le host du lobby."""
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
    
    # Mettre à jour le joueur par le host
    payload = get_base_player_update_payload()
    response = await client.put(
        get_update_player_url(player.id),
        json=payload,
        headers=get_auth_headers(token1)  # token du host
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == payload["score"]


# 404 - Not Found
@pytest.mark.asyncio
async def test_update_player_not_found(client, auth_service):
    """Test mise à jour d'un joueur inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    payload = get_base_player_update_payload()
    response = await client.put(
        get_update_player_url(fake_id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


# 403 - Forbidden (pas le joueur ni le host)
@pytest.mark.asyncio
async def test_update_player_forbidden(client, auth_service, db_session):
    """Test mise à jour d'un joueur par un utilisateur non autorisé."""
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
    
    # Tenter de mettre à jour avec user3 qui n'est ni le joueur ni le host
    payload = get_base_player_update_payload()
    response = await client.put(
        get_update_player_url(player.id),
        json=payload,
        headers=get_auth_headers(token3)  # token de user3
    )
    
    assert response.status_code == 403


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_update_player_invalid_uuid(client, auth_service):
    """Test mise à jour d'un joueur avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    payload = get_base_player_update_payload()
    response = await client.put(
        get_update_player_url("invalid-uuid"),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_update_player_unauthorized(client, auth_service, db_session):
    """Test mise à jour d'un joueur sans authentification."""
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
    
    payload = get_base_player_update_payload()
    response = await client.put(
        get_update_player_url(player.id),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

