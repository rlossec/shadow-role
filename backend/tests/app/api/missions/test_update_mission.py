"""
Tests pour l'endpoint PUT /api/missions/{mission_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/missions/test_update_mission.py -v
"""
import pytest
from uuid import uuid4

from app.models.game import GameTypeEnum
from app.schemas import GameCreate
from app.schemas.mission import MissionCreate
from app.repositories import GameRepository, MissionRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.missions.helpers import get_base_mission_update_payload, get_update_mission_url


# 200 - Success
@pytest.mark.asyncio
async def test_update_mission_success(client, auth_service, db_session):
    """Test mise à jour d'une mission avec succès."""
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
    
    # Mettre à jour la mission
    payload = get_base_mission_update_payload()
    response = await client.put(
        get_update_mission_url(mission.id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["difficulty"] == payload["difficulty"]


@pytest.mark.asyncio
async def test_update_mission_partial(client, auth_service, db_session):
    """Test mise à jour partielle d'une mission."""
    _, token = await create_user_and_get_token(client, auth_service)
    
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
    
    # Mettre à jour avec un payload partiel
    response = await client.put(
        get_update_mission_url(mission.id),
        json={
            "title": "Updated Mission",
            "difficulty": 75
        },
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Mission"
    assert data["difficulty"] == 75


@pytest.mark.asyncio
async def test_update_mission_empty_payload(client, auth_service, db_session):
    """Test mise à jour d'une mission avec un payload vide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
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
        title="Original Mission",
        description="Original description",
        difficulty=50,
        game_id=game.id
    ))
    
    # Mettre à jour avec un payload vide
    response = await client.put(
        get_update_mission_url(mission.id),
        json={},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    # La mission doit exister même si aucun champ n'est mis à jour
    data = response.json()
    assert data["id"] == str(mission.id)


# 404 - Not Found
@pytest.mark.asyncio
async def test_update_mission_not_found(client, auth_service):
    """Test mise à jour d'une mission inexistante."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    payload = get_base_mission_update_payload()
    response = await client.put(
        get_update_mission_url(fake_id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_update_mission_invalid_uuid(client, auth_service):
    """Test mise à jour d'une mission avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    payload = get_base_mission_update_payload()
    response = await client.put(
        get_update_mission_url("invalid-uuid"),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_update_mission_unauthorized(client, auth_service, db_session):
    """Test mise à jour d'une mission sans authentification."""
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
    
    payload = get_base_mission_update_payload()
    response = await client.put(
        get_update_mission_url(mission.id),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

