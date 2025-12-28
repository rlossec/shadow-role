"""
Tests pour l'endpoint POST /api/lobbies.

Pour exécuter ces tests:
    uv run pytest tests/app/api/lobbies/test_create_lobby.py -v
    uv run pytest tests/app/api/lobbies/test_create_lobby.py::test_create_lobby_success -v
"""
import pytest
from uuid import uuid4

from app.models.game import GameTypeEnum
from app.schemas import GameCreate
from app.models import LobbyStatus
from app.repositories import GameRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.lobbies.helpers import get_base_lobby_create_payload, get_create_lobby_url

# Les champs obligatoires pour LobbyCreate sont: name, game_id
REQUIRED_FIELDS = ["name", "game_id"]


# 201 - Success
@pytest.mark.asyncio
async def test_create_lobby_success(client, auth_service, db_session):
    """Test création d'un lobby avec succès."""
    user, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    # Créer un lobby avec le payload de base
    payload = get_base_lobby_create_payload(str(game.id))
    response = await client.post(
        get_create_lobby_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["host_id"] == str(user.id)
    assert data["status"] == LobbyStatus.WAITING.value
    assert "code" in data
    assert data["game_id"] == str(game.id)
    assert data["min_players"] == payload["min_players"]
    assert data["max_players"] == payload["max_players"]


# 422 - Unprocessable Entity (champs obligatoires manquants)
@pytest.mark.asyncio
@pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
async def test_create_lobby_missing_required_fields(
    client, auth_service, db_session, missing_field
):
    """
    Test création d'un lobby avec un champ obligatoire manquant.
    
    Ce test itère automatiquement sur tous les champs obligatoires
    pour s'assurer que chacun génère une erreur appropriée.
    """
    _, token = await create_user_and_get_token(client, auth_service)
    
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    payload = get_base_lobby_create_payload(str(game.id))
    del payload[missing_field]  # Enlever le champ obligatoire
    
    response = await client.post(
        get_create_lobby_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Vérifier que l'erreur mentionne le champ manquant
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    assert missing_field in error_fields


@pytest.mark.asyncio
async def test_create_lobby_missing_all_required_fields(client, auth_service):
    """Test création d'un lobby sans aucun champ obligatoire."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.post(
        get_create_lobby_url(),
        json={},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    # Tous les champs obligatoires doivent être présents dans les erreurs
    for required_field in REQUIRED_FIELDS:
        assert required_field in error_fields


# 404 - Not Found
@pytest.mark.asyncio
async def test_create_lobby_game_not_found(client, auth_service):
    """Test création d'un lobby avec un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_game_id = uuid4()
    payload = get_base_lobby_create_payload(str(fake_game_id))
    
    response = await client.post(
        get_create_lobby_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "game" in response.json()["detail"].lower()


# 401 - Unauthorized (pas de token)
@pytest.mark.asyncio
async def test_create_lobby_unauthorized(client, db_session):
    """Test création d'un lobby sans authentification."""

    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    payload = get_base_lobby_create_payload(str(game.id))
    
    response = await client.post(
        get_create_lobby_url(),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

