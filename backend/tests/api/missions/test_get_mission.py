"""
Tests pour l'endpoint GET /api/missions/{mission_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/missions/test_get_mission.py -v
"""
import pytest
from uuid import uuid4

from schemas import GameCreate
from schemas.mission import MissionCreate
from repositories import GameRepository, MissionRepository
from tests.api.helpers import create_user_and_get_token, get_auth_headers
from tests.api.missions.helpers import get_mission_url


# 200 - Success
@pytest.mark.asyncio
async def test_get_mission_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'une mission avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu et une mission
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
    
    mission_repo = MissionRepository(db_session)
    mission = await mission_repo.create_mission(MissionCreate(
        title="Test Mission",
        description="Test description",
        difficulty=50,
        game_id=game.id
    ))
    
    # Récupérer la mission
    response = await client.get(
        get_mission_url(mission.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(mission.id)
    assert data["title"] == "Test Mission"


# 404 - Not Found
@pytest.mark.asyncio
async def test_get_mission_not_found(client, auth_service):
    """Test récupération d'une mission inexistante."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        get_mission_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_get_mission_invalid_uuid(client, auth_service):
    """Test récupération d'une mission avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_mission_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_get_mission_unauthorized(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'une mission sans authentification."""
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
    
    mission_repo = MissionRepository(db_session)
    mission = await mission_repo.create_mission(MissionCreate(
        title="Test Mission",
        description="Test description",
        difficulty=50,
        game_id=game.id
    ))
    
    response = await client.get(
        get_mission_url(mission.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

