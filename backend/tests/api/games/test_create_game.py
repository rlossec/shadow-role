"""
Tests pour l'endpoint POST /api/games.

Pour exécuter ces tests:
    uv run pytest tests/api/games/test_create_game.py -v
"""
import pytest

from tests.api.helpers import create_user_and_get_token, get_auth_headers
from tests.api.games.helpers import get_base_game_create_payload, get_create_game_url

# Les champs obligatoires pour GameCreate sont: name, description, game_type_id
REQUIRED_FIELDS = ["name", "description", "game_type_id"]


# 201 - Success
@pytest.mark.asyncio
async def test_create_game_success(client, auth_service, db_session, initialized_game_types):
    """Test création d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    # Créer un jeu avec le payload de base
    payload = get_base_game_create_payload(str(mission_type.id))
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
async def test_create_game_missing_required_field(client, auth_service, initialized_game_types, field):
    """Test création d'un jeu avec un champ obligatoire manquant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
    payload = get_base_game_create_payload(str(mission_type.id))
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


# 404 - Not Found (game_type_id inexistant)
@pytest.mark.asyncio
async def test_create_game_invalid_game_type(client, auth_service):
    """Test création d'un jeu avec un game_type_id inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    from uuid import uuid4
    fake_game_type_id = uuid4()
    
    payload = get_base_game_create_payload(str(fake_game_type_id))
    response = await client.post(
        get_create_game_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    # Le statut peut être 404 ou 422 selon la validation
    assert response.status_code in [404, 422]


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_create_game_unauthorized(client, initialized_game_types):
    """Test création d'un jeu sans authentification."""
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
    payload = get_base_game_create_payload(str(mission_type.id))
    response = await client.post(
        get_create_game_url(),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

