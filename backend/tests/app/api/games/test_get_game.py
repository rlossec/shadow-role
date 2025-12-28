"""
Tests pour l'endpoint GET /api/games/{game_id}.

Pour exécuter ces tests:
    uv run pytest tests/app/api/games/test_get_game.py -v
"""
import pytest
from uuid import uuid4

from app.models.game import GameTypeEnum
from app.schemas import GameCreate
from app.repositories import GameRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.games.helpers import get_game_url


# 200 - Success
@pytest.mark.asyncio
async def test_get_game_success(client, auth_service, db_session):
    """Test récupération d'un jeu avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    # Créer un jeu
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        min_players=2,
        max_players=10,
        game_type=GameTypeEnum.MISSION,
    ))
    
    # Récupérer le jeu
    response = await client.get(
        get_game_url(game.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(game.id)
    assert data["name"] == "Test Game"


# 404 - Not Found
@pytest.mark.asyncio
async def test_get_game_not_found(client, auth_service):
    """Test récupération d'un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.get(
        get_game_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_get_game_invalid_uuid(client, auth_service):
    """Test récupération d'un jeu avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.get(
        get_game_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_get_game_unauthorized(client, auth_service, db_session):
    """Test récupération d'un jeu sans authentification."""
    
    game_repo = GameRepository(db_session)
    game = await game_repo.create_game(GameCreate(
        name="Test Game",
        description="Test description",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    
    response = await client.get(
        get_game_url(game.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

