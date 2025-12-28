"""
Tests pour l'endpoint PUT /api/lobbies/{lobby_id}.

Pour exécuter ces tests:
    uv run pytest tests/app/api/lobbies/test_update_lobby.py -v
"""
import pytest
from uuid import uuid4

from app.models.game import GameTypeEnum
from app.schemas import GameCreate, LobbyCreate
from app.repositories import GameRepository, LobbyRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.lobbies.helpers import get_base_lobby_update_payload, get_update_lobby_url


# 200 - Success
@pytest.mark.asyncio
async def test_update_lobby_success(client, auth_service, db_session):
    """Test mise à jour d'un lobby avec succès."""
    user, token = await create_user_and_get_token(client, auth_service)

    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    game_2 = await game_repo.create_game(GameCreate(
        name="Test Game 2",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))

    lobby_repo = LobbyRepository(db_session)
    lobby = await lobby_repo.create_lobby(
        LobbyCreate(name="Original Lobby", game_id=game.id, min_players=2, max_players=10),
        user.id
    )
    
    # Mettre à jour le lobby
    payload = get_base_lobby_update_payload(str(game_2.id))
    response = await client.put(
        get_update_lobby_url(lobby.id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(lobby.id)
    assert data["name"] == payload["name"]
    assert data["game_id"] == str(game_2.id)
    assert data["min_players"] == payload["min_players"]
    assert data["max_players"] == payload["max_players"]


@pytest.mark.asyncio
async def test_update_lobby_partial_update(client, auth_service, db_session):
    """Test mise à jour partielle d'un lobby (seulement le nom)."""
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
        LobbyCreate(name="Original Lobby", game_id=game.id, min_players=2, max_players=10),
        user.id
    )
    
    # Mettre à jour seulement le nom
    payload = {"name": "Updated Name Only"}
    response = await client.put(
        get_update_lobby_url(lobby.id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name Only"
    # Les autres champs doivent rester inchangés (vérifier les valeurs par défaut)
    assert data["min_players"] == 2
    assert data["max_players"] == 10


@pytest.mark.asyncio
async def test_update_lobby_empty_payload(client, auth_service, db_session):
    """Test mise à jour avec un payload vide (tous les champs sont optionnels)."""
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
        LobbyCreate(name="Original Lobby", game_id=game.id, min_players=2, max_players=10),
        user.id
    )
    
    # Mettre à jour avec un payload vide
    response = await client.put(
        get_update_lobby_url(lobby.id),
        json={},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    # Le lobby doit exister même si aucun champ n'est mis à jour
    data = response.json()
    assert data["id"] == str(lobby.id)


# 404 - Not Found
@pytest.mark.asyncio
async def test_update_lobby_not_found(client, auth_service):
    """Test mise à jour d'un lobby inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    payload = get_base_lobby_update_payload(str(fake_id))
    
    response = await client.put(
        get_update_lobby_url(fake_id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 403  # 403 car le lobby n'existe pas donc l'utilisateur n'est pas le host


# 403 - Forbidden (pas le host)
@pytest.mark.asyncio
async def test_update_lobby_not_host(client, auth_service, db_session):
    """Test mise à jour d'un lobby par un joueur qui n'est pas le host."""
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
    
    # Tenter de mettre à jour avec user2 qui n'est pas le host
    payload = get_base_lobby_update_payload(str(game.id))
    response = await client.put(
        get_update_lobby_url(lobby.id),
        json=payload,
        headers=get_auth_headers(token2)  # token de user2
    )
    
    assert response.status_code == 403
    assert "host" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_update_lobby_invalid_uuid(client, auth_service):
    """Test mise à jour d'un lobby avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    payload = get_base_lobby_update_payload(str(fake_id))
    response = await client.put(
        get_update_lobby_url("invalid-uuid"),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_update_lobby_unauthorized(client, auth_service, db_session):
    """Test mise à jour d'un lobby sans authentification."""
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
    
    payload = get_base_lobby_update_payload(str(game.id))
    response = await client.put(
        get_update_lobby_url(lobby.id),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

