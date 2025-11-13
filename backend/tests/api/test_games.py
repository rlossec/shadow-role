"""
Tests pour les endpoints /api/games.

shortcut : uv run pytest tests/api/test_games.py -v
"""
import pytest
from uuid import uuid4

from tests.api.helpers import create_user_and_get_token, get_auth_headers

from schemas import GameCreate

from repositories.game_repository import GameRepository
from repositories.mission_repository import MissionRepository

# Test List Games
@pytest.mark.asyncio
async def test_list_games_success(client, auth_service, db_session, initialized_game_types):
    """Test liste des jeux avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)

    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    role_type = game_types[1]     # Deuxième type (Role)

    # Créer des jeux
    game_repo = GameRepository(db_session)
    game1 = await game_repo.create_game(GameCreate(
        name="Game 1",
        description="Test 1",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    game2 = await game_repo.create_game(GameCreate(
        name="Game 2",
        description="Test 2",
        game_type_id=role_type.id,
        min_players=3,
        max_players=12,
    ))
    
    # Lister les jeux
    response = await client.get(
        "/api/games",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    game_ids = [g["id"] for g in data]
    assert str(game1.id) in game_ids
    assert str(game2.id) in game_ids


@pytest.mark.asyncio
async def test_list_games_with_pagination(client, auth_service, db_session, initialized_game_types):
    """Test liste des jeux avec pagination."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
    # Créer des jeux
    game_repo = GameRepository(db_session)
    for i in range(5):
        await game_repo.create_game(GameCreate(
            name=f"Game {i}",
            description=f"Test {i}",
            game_type_id=mission_type.id,
            min_players=2,
            max_players=10
        ))
    
    # Lister les jeux avec limite
    response = await client.get(
        "/api/games?skip=0&limit=2",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2

# Test create game
@pytest.mark.asyncio
async def test_create_game_success(client, auth_service, db_session, initialized_game_types):
    """Test création d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    # Créer un jeu
    response = await client.post(
        "/api/games",
        json={
            "name": "Test Game",
            "description": "Test description",
            "min_players": 2,
            "max_players": 10,
            "game_type_id": str(mission_type.id),
        },
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Game"
    assert data["description"] == "Test description"
    assert data["min_players"] == 2
    assert data["max_players"] == 10
    assert "id" in data


@pytest.mark.asyncio
async def test_create_game_unauthorized(client, initialized_game_types):
    """Test création d'un jeu sans authentification."""
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    response = await client.post(
        "/api/games",
        json={
            "name": "Test Game",
            "description": "Test description",
            "game_type_id": str(mission_type.id),
            "min_players": 2,
            "max_players": 10
        }
    )
    
    assert response.status_code == 401


# Test get game
@pytest.mark.asyncio
async def test_get_game_success(client, auth_service, db_session, initialized_game_types):
    """Test récupération d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    # Créer un jeu
    from repositories.game_repository import GameRepository
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        min_players=2,
        max_players=10,
        game_type_id=mission_type.id
    ))
    
    # Récupérer le jeu
    response = await client.get(
        f"/api/games/{game.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(game.id)
    assert data["name"] == "Test Game"


@pytest.mark.asyncio
async def test_get_game_not_found(client, auth_service):
    """Test récupération d'un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        f"/api/games/{fake_id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# Test update game
@pytest.mark.asyncio
async def test_update_game_success(client, auth_service, db_session, initialized_game_types):
    """Test mise à jour d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    # Créer un jeu
    from repositories.game_repository import GameRepository
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Mettre à jour le jeu
    response = await client.put(
        f"/api/games/{game.id}",
        json={
            "name": "Updated Game",
            "min_players": 3
        },
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Game"
    assert data["min_players"] == 3
    assert data["max_players"] == 10  # Non modifié



@pytest.mark.asyncio
async def test_update_game_not_found(client, auth_service):
    """Test mise à jour d'un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.put(
        f"/api/games/{fake_id}",
        json={"name": "Updated Game"},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


# Test delete game
@pytest.mark.asyncio
async def test_delete_game_success(client, auth_service, db_session, initialized_game_types):
    """Test suppression d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        min_players=2,
        max_players=10,
        game_type_id=mission_type.id
    ))
    
    # Supprimer le jeu
    response = await client.delete(
        f"/api/games/{game.id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 204
    
    # Vérifier que le jeu n'existe plus
    response = await client.get(
        f"/api/games/{game.id}",
        headers=get_auth_headers(token)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_game_not_found(client, auth_service):
    """Test suppression d'un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.delete(
        f"/api/games/{fake_id}",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


# @pytest.mark.asyncio
# async def test_get_game_missions_success(client, auth_service, db_session, initialized_game_types):
#     """Test récupération des missions d'un jeu avec succès."""
#     _, token = await create_user_and_get_token(client, auth_service)
    
#     # Récupérer les types de jeu initialisés
#     _, game_types = initialized_game_types
#     mission_type = game_types[0]  # Premier type (Mission)
    
#     # Créer un jeu et des missions 
#     game_repo = GameRepository(db_session)
#     game = await game_repo.create_game(GameCreate(
#         name="Test Game",
#         description="Test",
#         min_players=2,
#         max_players=10,
#         game_type_id=mission_type.id
#     ))
    
#     from schemas.mission import MissionCreate
#     mission_repo = MissionRepository(db_session)
#     mission1 = await mission_repo.create_mission(MissionCreate(
#         title="Mission 1",
#         description="Test",
#         difficulty=50,
#         game_id=game.id
#     ))
#     mission2 = await mission_repo.create_mission(MissionCreate(
#         title="Mission 2",
#         description="Test",
#         difficulty=75,
#         game_id=game.id
#     ))
    
#     # Récupérer les missions du jeu
#     response = await client.get(
#         f"/api/games/{game.id}/missions",
#         headers=get_auth_headers(token)
#     )
    
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     mission_ids = [m["id"] for m in data]
#     assert str(mission1.id) in mission_ids
#     assert str(mission2.id) in mission_ids


# @pytest.mark.asyncio
# async def test_get_game_missions_game_not_found(client, auth_service):
#     """Test récupération des missions d'un jeu inexistant."""
#     _, token = await create_user_and_get_token(client, auth_service)
    
#     fake_id = uuid4()
#     response = await client.get(
#         f"/api/games/{fake_id}/missions",
#         headers=get_auth_headers(token)
#     )
    
#     assert response.status_code == 404

