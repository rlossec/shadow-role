"""
Tests pour les endpoints /api/missions.

shortcut : uv run pytest tests/api/test_missions.py -v
"""
import pytest
from uuid import uuid4

from schemas import GameCreate, MissionCreate, MissionUpdate
from tests.api.helpers import create_user_and_get_token, get_auth_headers


@pytest.mark.asyncio
async def test_create_mission_success(client, auth_service, db_session, initialized_game_types):
    """Test création d'une mission avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu
    from repositories.game_repository import GameRepository
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Créer une mission
    response = await client.post(
        "/api/missions",
        json={
            "title": "Test Mission",
            "description": "Test description",
            "difficulty": 50,
            "game_id": str(game.id)
        },
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Mission"
    assert data["description"] == "Test description"
    assert data["difficulty"] == 50
    assert data["game_id"] == str(game.id)


@pytest.mark.asyncio
async def test_create_mission_unauthorized(client, db_session, initialized_game_types):
    """Test création d'une mission sans authentification."""
    # Créer un jeu
    from repositories.game_repository import GameRepository
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    response = await client.post(
        "/api/missions",
        json={
            "title": "Test Mission",
            "description": "Test description",
            "difficulty": 50,
            "game_id": str(game.id)
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_mission_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'une mission avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu et une mission
    from repositories.game_repository import GameRepository
    from repositories.mission_repository import MissionRepository
    
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    from schemas.mission import MissionCreate
    mission_repo = MissionRepository(db_session)
    mission = await mission_repo.create_mission(MissionCreate(
        title="Test Mission",
        description="Test description",
        difficulty=50,
        game_id=game.id
    ))
    
    # Récupérer la mission
    response = await client.get(
        f"/api/missions/{mission.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(mission.id)
    assert data["title"] == "Test Mission"


@pytest.mark.asyncio
async def test_get_mission_not_found(client, auth_service):
    """Test récupération d'une mission inexistante."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        f"/api/missions/{fake_id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_mission_success(client, auth_service, db_session, initialized_game_types):
    """Test mise à jour d'une mission avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu et une mission
    from repositories.game_repository import GameRepository
    from repositories.mission_repository import MissionRepository
    
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    from schemas.mission import MissionCreate
    mission_repo = MissionRepository(db_session)
    mission = await mission_repo.create_mission(MissionCreate(
        title="Test Mission",
        description="Test description",
        difficulty=50,
        game_id=game.id
    ))
    
    # Mettre à jour la mission
    response = await client.put(
        f"/api/missions/{mission.id}",
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
async def test_update_mission_not_found(client, auth_service):
    """Test mise à jour d'une mission inexistante."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.put(
        f"/api/missions/{fake_id}",
        json={"title": "Updated Mission"},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_mission_success(client, auth_service, db_session, initialized_game_types):
    """Test suppression d'une mission avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu et une mission
    from repositories.game_repository import GameRepository
    from repositories.mission_repository import MissionRepository
    
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    from schemas.mission import MissionCreate
    mission_repo = MissionRepository(db_session)
    mission = await mission_repo.create_mission(MissionCreate(
        title="Test Mission",
        description="Test description",
        difficulty=50,
        game_id=game.id
    ))
    
    # Supprimer la mission
    response = await client.delete(
        f"/api/missions/{mission.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 204
    
    # Vérifier que la mission n'existe plus
    response = await client.get(
        f"/api/missions/{mission.id}",
        headers=get_auth_headers(token)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_mission_not_found(client, auth_service):
    """Test suppression d'une mission inexistante."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.delete(
        f"/api/missions/{fake_id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_missions_by_game_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération des missions d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu et des missions
    from repositories.game_repository import GameRepository
    from repositories.mission_repository import MissionRepository
    
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    from schemas.mission import MissionCreate
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
        f"/api/missions/game/{game.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    mission_ids = [m["id"] for m in data]
    assert str(mission1.id) in mission_ids
    assert str(mission2.id) in mission_ids


@pytest.mark.asyncio
async def test_get_missions_by_game_empty(client, auth_service, db_session, initialized_game_types):
    """Test récupération des missions d'un jeu sans missions."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu sans missions
    from repositories.game_repository import GameRepository
    game_repo = GameRepository(db_session)
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Récupérer les missions du jeu
    response = await client.get(
        f"/api/missions/game/{game.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

