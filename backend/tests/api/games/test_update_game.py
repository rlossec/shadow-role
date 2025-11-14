"""
Tests pour l'endpoint PUT /api/games/{game_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/games/test_update_game.py -v
"""
import pytest
from uuid import uuid4

from schemas import GameCreate
from repositories import GameRepository
from tests.api.helpers import create_user_and_get_token, get_auth_headers
from tests.api.games.helpers import get_base_game_update_payload, get_update_game_url


# 200 - Success
@pytest.mark.asyncio
async def test_update_game_success(client, auth_service, db_session, initialized_game_types):
    """Test mise à jour d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Récupérer les types de jeu initialisés
    _, game_types = initialized_game_types
    mission_type = game_types[0]  # Premier type (Mission)
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Mettre à jour le jeu
    payload = get_base_game_update_payload()
    response = await client.put(
        get_update_game_url(game.id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["min_players"] == payload["min_players"]
    assert data["max_players"] == payload["max_players"]


@pytest.mark.asyncio
async def test_update_game_partial(client, auth_service, db_session, initialized_game_types):
    """Test mise à jour partielle d'un jeu."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Mettre à jour avec un payload partiel
    response = await client.put(
        get_update_game_url(game.id),
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
async def test_update_game_empty_payload(client, auth_service, db_session, initialized_game_types):
    """Test mise à jour d'un jeu avec un payload vide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Original Game",
        description="Original description",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    # Mettre à jour avec un payload vide
    response = await client.put(
        get_update_game_url(game.id),
        json={},
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    # Le jeu doit exister même si aucun champ n'est mis à jour
    data = response.json()
    assert data["id"] == str(game.id)


# 404 - Not Found
@pytest.mark.asyncio
async def test_update_game_not_found(client, auth_service):
    """Test mise à jour d'un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    payload = get_base_game_update_payload()
    response = await client.put(
        get_update_game_url(fake_id),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_update_game_invalid_uuid(client, auth_service):
    """Test mise à jour d'un jeu avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    payload = get_base_game_update_payload()
    response = await client.put(
        get_update_game_url("invalid-uuid"),
        json=payload,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_update_game_unauthorized(client, auth_service, db_session, initialized_game_types):
    """Test mise à jour d'un jeu sans authentification."""
    _, game_types = initialized_game_types
    mission_type = game_types[0]
    
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        game_type_id=mission_type.id,
        min_players=2,
        max_players=10
    ))
    
    payload = get_base_game_update_payload()
    response = await client.put(
        get_update_game_url(game.id),
        json=payload
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

