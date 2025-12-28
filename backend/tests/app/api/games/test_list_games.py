"""
Tests pour l'endpoint GET /api/games.

Pour exécuter ces tests:
    uv run pytest tests/api/games/test_list_games.py -v
"""
import pytest

from app.models.game import GameTypeEnum
from app.schemas import GameCreate
from app.repositories import GameRepository
from tests.app.api.helpers import create_user_and_get_token, get_auth_headers
from tests.app.api.games.helpers import get_games_url


# 200 - Success
@pytest.mark.asyncio
async def test_list_games_success(client, auth_service, db_session):
    """Test liste des jeux avec succès."""
    _, token = await create_user_and_get_token(client, auth_service)

    # Créer des jeux
    game_repo = GameRepository(db_session)
    game1 = await game_repo.create_game(GameCreate(
        name="Game 1",
        description="Test 1",
        game_type=GameTypeEnum.MISSION,
        min_players=2,
        max_players=10
    ))
    game2 = await game_repo.create_game(GameCreate(
        name="Game 2",
        description="Test 2",
        game_type=GameTypeEnum.ROLE,
        min_players=3,
        max_players=12,
    ))
    
    # Lister les jeux
    response = await client.get(
        get_games_url(),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    game_ids = [g["id"] for g in data]
    assert str(game1.id) in game_ids
    assert str(game2.id) in game_ids


@pytest.mark.asyncio
async def test_list_games_with_pagination(client, auth_service, db_session):
    """Test liste des jeux avec pagination."""
    _, token = await create_user_and_get_token(client, auth_service)

    # Créer des jeux
    game_repo = GameRepository(db_session)
    for i in range(5):
        await game_repo.create_game(GameCreate(
            name=f"Game {i}",
            description=f"Test {i}",
            game_type=GameTypeEnum.MISSION,
            min_players=2,
            max_players=10
        ))
    
    # Lister les jeux avec limite
    response = await client.get(
        f"{get_games_url()}?skip=0&limit=2",
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_list_games_unauthorized(client):
    """Test liste des jeux sans authentification."""
    response = await client.get(
        get_games_url()
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

