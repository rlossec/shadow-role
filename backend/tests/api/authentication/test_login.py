"""
Tests pour l'endpoint POST /auth/jwt/login.

Pour exécuter ces tests:
    uv run pytest tests/api/authentication/test_login.py -v
    uv run pytest tests/api/authentication/test_login.py::test_login_success_with_username -v
"""
import pytest
from sqlalchemy import select

from models import User
from api.authentication import LOGIN_BAD_CREDENTIALS
from tests.api.authentication.helpers import (
    get_base_login_form_data,
    get_base_login_headers,
    LOGIN_REQUIRED_FIELDS,
    create_active_user,
)


# 200 - Success
@pytest.mark.asyncio
async def test_login_success_with_username(client, auth_service):
    """Test connexion réussie avec username."""
    await create_active_user(auth_service, "logintest", "login@example.com", "password123")
    
    form_data = get_base_login_form_data(username="logintest", password="password123")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_login_success_with_email(client, auth_service):
    """Test connexion réussie avec email."""
    await create_active_user(auth_service, "logintest2", "login2@example.com", "password123")
    
    form_data = get_base_login_form_data(username="login2@example.com", password="password123")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_login_username_vs_email_same_value(client, auth_service):
    """Test que le login fonctionne à la fois avec username et email."""
    await create_active_user(auth_service, "samevalue", "samevalue@example.com", "password123")
    
    # Login avec username
    form_data = get_base_login_form_data(username="samevalue", password="password123")
    response1 = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    assert response1.status_code == 200
    
    # Login avec email
    form_data = get_base_login_form_data(username="samevalue@example.com", password="password123")
    response2 = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    assert response2.status_code == 200


# 400 - Bad Request (mauvais identifiants)
@pytest.mark.asyncio
async def test_login_wrong_password(client, auth_service):
    """Test connexion avec un mauvais mot de passe."""
    await create_active_user(auth_service, "logintest3", "login3@example.com", "password123")
    
    form_data = get_base_login_form_data(username="logintest3", password="wrongpassword")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    
    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert "LOGIN_BAD_CREDENTIALS" in error_detail or "invalid" in error_detail.lower() or "incorrect" in error_detail.lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test connexion avec un utilisateur inexistant (username)."""
    form_data = get_base_login_form_data(username="nonexistent", password="password123")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    
    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert "LOGIN_BAD_CREDENTIALS" in error_detail or "invalid" in error_detail.lower() or "incorrect" in error_detail.lower()


@pytest.mark.asyncio
async def test_login_nonexistent_email(client):
    """Test connexion avec un utilisateur inexistant (email)."""
    form_data = get_base_login_form_data(username="nonexistent@example.com", password="password123")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    
    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert "LOGIN_BAD_CREDENTIALS" in error_detail or "invalid" in error_detail.lower() or "incorrect" in error_detail.lower()


@pytest.mark.asyncio
async def test_login_inactive_user(client, auth_service, db_session):
    """Test connexion avec un utilisateur inactif."""
    user = await create_active_user(auth_service, "inactive", "inactive@example.com", "password123")
    
    # Désactiver l'utilisateur
    result = await db_session.execute(select(User).where(User.id == user.id))
    db_user = result.scalar_one()
    db_user.is_active = False
    await db_session.commit()
    await db_session.refresh(db_user)
    
    form_data = get_base_login_form_data(username="inactive", password="password123")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    
    assert response.status_code in (400, 401)
    error_detail = response.json()["detail"]
    assert error_detail == LOGIN_BAD_CREDENTIALS


# 422 - Unprocessable Entity (champs obligatoires manquants)
@pytest.mark.asyncio
@pytest.mark.parametrize("missing_field", LOGIN_REQUIRED_FIELDS)
async def test_login_missing_required_fields(client, missing_field):
    """
    Test connexion avec un champ obligatoire manquant.
    
    Ce test itère automatiquement sur tous les champs obligatoires
    pour s'assurer que chacun génère une erreur appropriée.
    """
    form_data = get_base_login_form_data()
    del form_data[missing_field]  # Enlever le champ obligatoire
    
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    
    assert response.status_code == 422


# 400 - Bad Request (champs vides)
@pytest.mark.asyncio
async def test_login_empty_credentials(client):
    """Test connexion avec des credentials vides."""
    # Username vide
    form_data = get_base_login_form_data(username="", password="password123")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    assert response.status_code == 400
    
    # Password vide
    form_data = get_base_login_form_data(username="testuser", password="")
    response = await client.post(
        "/auth/jwt/login",
        data=form_data,
        headers=get_base_login_headers()
    )
    assert response.status_code == 400
