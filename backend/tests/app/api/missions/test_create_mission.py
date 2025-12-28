"""
Tests pour l'endpoint POST /api/missions.

Pour exécuter ces tests:
    uv run pytest tests/app/api/missions/test_create_mission.py -v
"""
import pytest

from app.models.game import GameTypeEnum
from app.schemas import GameCreate
from app.repositories import GameRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.missions.helpers import get_base_mission_create_payload, get_create_mission_url

# Les champs obligatoires pour MissionCreate sont: title, description, difficulty, game_id
REQUIRED_FIELDS = ["title", "description", "difficulty", "game_id"]


# 201 - Success
@pytest.mark.asyncio
async def test_create_mission_success(client, auth_service, db_session):
    """Test création d'une mission avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    # Créer une mission avec le payload de base
    payload = get_base_mission_create_payload(str(game.id))
    response = await client.post(
        get_create_mission_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["difficulty"] == payload["difficulty"]
    assert data["game_id"] == payload["game_id"]


# 422 - Unprocessable Entity (champs manquants)
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
@pytest.mark.asyncio
async def test_create_mission_missing_required_field(client, auth_service, db_session, field):
    """Test création d'une mission avec un champ obligatoire manquant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    payload = get_base_mission_create_payload(str(game.id))
    # Enlever le champ obligatoire
    payload.pop(field)
    
    response = await client.post(
        get_create_mission_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    assert field in error_fields


@pytest.mark.asyncio
async def test_create_mission_missing_all_required_fields(client, auth_service):
    """Test création d'une mission sans aucun champ obligatoire."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.post(
        get_create_mission_url(),
        json={},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    # Tous les champs obligatoires doivent être présents dans les erreurs
    for field in REQUIRED_FIELDS:
        assert field in error_fields


# 404 - Not Found (game_id inexistant)
@pytest.mark.asyncio
async def test_create_mission_invalid_game_id(client, auth_service):
    """Test création d'une mission avec un game_id inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    from uuid import uuid4
    fake_game_id = uuid4()
    
    payload = get_base_mission_create_payload(str(fake_game_id))
    response = await client.post(
        get_create_mission_url(),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    # Le statut peut être 404 ou 422 selon la validation
    assert response.status_code in [404, 422]


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_create_mission_unauthorized(client, db_session):
    """Test création d'une mission sans authentification."""
    # Créer un jeu
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    payload = get_base_mission_create_payload(str(game.id))
    response = await client.post(
        get_create_mission_url(),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

