"""
Tests pour l'endpoint POST /api/games.

Pour exécuter ces tests:
    uv run pytest tests/api/games/test_create_game.py -v
"""
import pytest

from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.games.helpers import get_base_game_create_payload, get_create_game_url

# Les champs obligatoires pour GameCreate sont: name
REQUIRED_FIELDS = ["name"]


# 201 - Success
@pytest.mark.asyncio
async def test_create_game_success(client, auth_service, db_session):
    """Test création d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    
    # Créer un jeu avec le payload de base
    payload = get_base_game_create_payload()
    response = await client.post(
        get_create_game_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["min_players"] == payload["min_players"]
    assert data["max_players"] == payload["max_players"]
    assert "id" in data


# 422 - Unprocessable Entity (champs manquants)
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
@pytest.mark.asyncio
async def test_create_game_missing_required_field(client, auth_service, field):
    """Test création d'un jeu avec un champ obligatoire manquant."""
    _, token = await create_user_and_get_token(client, auth_service)
    

    payload = get_base_game_create_payload()
    # Enlever le champ obligatoire
    payload.pop(field)
    
    response = await client.post(
        get_create_game_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    assert field in error_fields


@pytest.mark.asyncio
async def test_create_game_missing_all_required_fields(client, auth_service):
    """Test création d'un jeu sans aucun champ obligatoire."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.post(
        get_create_game_url(),
        json={},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    # Tous les champs obligatoires doivent être présents dans les erreurs
    for field in REQUIRED_FIELDS:
        assert field in error_fields



# 401 - Unauthorized
@pytest.mark.asyncio
async def test_create_game_unauthorized(client):
    """Test création d'un jeu sans authentification."""
    payload = get_base_game_create_payload()
    response = await client.post(
        get_create_game_url(),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

