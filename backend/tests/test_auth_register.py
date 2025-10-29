"""Tests for the /auth/register endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test d'enregistrement avec succès."""
    response = await client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "is_active" in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """Test que le même username ne peut pas être enregistré deux fois."""
    # Premier enregistrement
    await client.post(
        "/auth/register",
        data={
            "username": "duplicate",
            "email": "first@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Tentative de réenregistrement
    response = await client.post(
        "/auth/register",
        data={
            "username": "duplicate",
            "email": "second@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test que le même email ne peut pas être enregistré deux fois."""
    # Premier enregistrement
    await client.post(
        "/auth/register",
        data={
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Tentative de réenregistrement
    response = await client.post(
        "/auth/register",
        data={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test que les emails invalides sont rejetés."""
    response = await client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    """Test que les champs manquants sont rejetés."""
    # Missing field: password
    response = await client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "email": "test@example.com"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # FastAPI retourne 422 pour les erreurs de validation de formulaire
    assert response.status_code == 422
    
    # Missing field: email
    response = await client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 422
    
    # Missing field: username
    response = await client.post(
        "/auth/register",
        data={
            "email": "test@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 422

