"""
Tests pour l'endpoint DELETE /api/missions/{mission_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/missions/test_delete_mission.py -v
"""
import pytest
from uuid import uuid4

from app.models.game import GameTypeEnum
from app.schemas import GameCreate
from app.schemas.mission import MissionCreate
from app.repositories import GameRepository, MissionRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.missions.helpers import get_mission_url, get_delete_mission_url


# 204 - Success (No Content)
@pytest.mark.asyncio
async def test_delete_mission_success(client, auth_service, db_session):
    """Test suppression d'une mission avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu et une mission
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
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
    
    # Supprimer la mission
    response = await client.delete(
        get_delete_mission_url(mission.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 204
    
    # Vérifier que la mission n'existe plus
    response = await client.get(
        get_mission_url(mission.id),
        headers=get_auth_headers(token)
    )
    assert response.status_code == 404


# 404 - Not Found
@pytest.mark.asyncio
async def test_delete_mission_not_found(client, auth_service):
    """Test suppression d'une mission inexistante."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.delete(
        get_delete_mission_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_delete_mission_invalid_uuid(client, auth_service):
    """Test suppression d'une mission avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.delete(
        get_delete_mission_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_delete_mission_unauthorized(client, auth_service, db_session):
    """Test suppression d'une mission sans authentification."""
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
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
    
    response = await client.delete(
        get_delete_mission_url(mission.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

