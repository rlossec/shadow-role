"""
Tests pour l'endpoint GET /api/missions/game/{game_id}.

Pour exécuter ces tests:
    uv run pytest tests/app/api/missions/test_get_missions_by_game.py -v
"""
import pytest

from app.models.game import GameTypeEnum
from app.schemas import GameCreate
from app.schemas.mission import MissionCreate
from app.repositories import GameRepository, MissionRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.missions.helpers import get_missions_by_game_url


# 200 - Success
@pytest.mark.asyncio
async def test_get_missions_by_game_success(client, auth_service, db_session):
    """Test récupération des missions d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu et des missions
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    mission_repo = MissionRepository(db_session)
    mission1 = await mission_repo.create_mission(MissionCreate(
        title="Mission 1",
        description="Test",
        difficulty=50,
        game_id=game.id
    ))
    mission2 = await mission_repo.create_mission(MissionCreate(
        title="Mission 2",
        description="Test",
        difficulty=75,
        game_id=game.id
    ))
    
    # Récupérer les missions du jeu
    response = await client.get(
        get_missions_by_game_url(game.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    mission_ids = [m["id"] for m in data]
    assert str(mission1.id) in mission_ids
    assert str(mission2.id) in mission_ids


@pytest.mark.asyncio
async def test_get_missions_by_game_empty(client, auth_service, db_session):
    """Test récupération des missions d'un jeu sans missions."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu sans missions
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    # Récupérer les missions du jeu
    response = await client.get(
        get_missions_by_game_url(game.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_get_missions_by_game_invalid_uuid(client, auth_service):
    """Test récupération des missions avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_missions_by_game_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_get_missions_by_game_unauthorized(client, auth_service, db_session):
    """Test récupération des missions sans authentification."""
    game_repo = GameRepository(db_session)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    response = await client.get(
        get_missions_by_game_url(game.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

