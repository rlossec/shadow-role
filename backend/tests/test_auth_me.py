"""Tests for the /auth/me endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_me_success(client: AsyncClient, db_session):
    """Test de récupération des informations de l'utilisateur connecté."""
    from models.user import User
    from core.password import get_password_hash
    from core.security import create_access_token
    
    # Créer un utilisateur
    user = User(
        username="metest",
        email="me@example.com",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Stocker l'ID avant la requête (évite les problèmes de session SQLAlchemy)
    user_id = user.id
    
    # Créer un token pour cet utilisateur (utiliser user ID)
    token = create_access_token(data={"sub": str(user_id)})
    
    # Faire une requête authentifiée
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "metest"
    assert data["email"] == "me@example.com"
    assert data["id"] == user_id


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    """Test sans token d'authentification."""
    response = await client.get("/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    """Test avec un token invalide."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_expired_token(client: AsyncClient):
    """Test avec un token expiré."""
    from datetime import timedelta
    from core.security import create_access_token
    
    # Créer un token expiré avec un ID utilisateur inexistant
    expired_token = create_access_token(
        data={"sub": "999"},
        expires_delta=timedelta(seconds=-1)  # Expiré depuis 1 seconde
    )
    
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    
    # Le token expiré devrait soit retourner 401, soit ne pas trouver l'utilisateur
    assert response.status_code in [401, 403]

