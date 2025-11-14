"""
Tests pour l'endpoint DELETE /api/games/{game_id}.

Pour exécuter ces tests:
    uv run pytest tests/api/games/test_delete_game.py -v
"""
import pytest
from uuid import uuid4

from schemas import GameCreate
from repositories import GameRepository
from tests.api.helpers import create_user_and_get_token, get_auth_headers
from tests.api.games.helpers import get_game_url, get_delete_game_url


# 204 - Success (No Content)
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
        get_delete_game_url(game.id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 204
    assert response.content == b""  # Pas de contenu pour 204
    
    # Vérifier que le jeu n'existe plus
    response = await client.get(
        get_game_url(game.id),
        headers=get_auth_headers(token)
    )
    assert response.status_code == 404


# 404 - Not Found
@pytest.mark.asyncio
async def test_delete_game_not_found(client, auth_service):
    """Test suppression d'un jeu inexistant."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    fake_id = uuid4()
    response = await client.delete(
        get_delete_game_url(fake_id),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# 422 - Unprocessable Entity (UUID invalide)
@pytest.mark.asyncio
async def test_delete_game_invalid_uuid(client, auth_service):
    """Test suppression d'un jeu avec un UUID invalide."""
    _, token = await create_user_and_get_token(client, auth_service)
    
    response = await client.delete(
        get_delete_game_url("invalid-uuid"),
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == 422


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_delete_game_unauthorized(client, auth_service, db_session, initialized_game_types):
    """Test suppression d'un jeu sans authentification."""
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
    
    response = await client.delete(
        get_delete_game_url(game.id)
        # Pas de headers d'authentification
    )
    
    assert response.status_code == 401

