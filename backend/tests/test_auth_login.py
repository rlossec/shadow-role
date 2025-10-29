"""
Tests for the /auth/login endpoint.

short cut command to run the test:
uv run pytest tests/test_auth_login.py::test_login_success
uv run pytest tests/test_auth_login.py::test_login_wrong_password
uv run pytest tests/test_auth_login.py::test_login_nonexistent_user
uv run pytest tests/test_auth_login.py::test_login_inactive_user


"""

import pytest


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    """Test with successful login."""

    from schemas import UserCreate
    from core.password import get_password_hash
    from repositories.user_repository import UserRepository
    
    user = UserCreate(
        username="logintest",
        email="login@example.com",
        password="password123"
    )
    user_repository = UserRepository(db_session)
    await user_repository.create_user(user)
    
    response = await client.post(
        "/auth/token",
        data={
            "username": "logintest",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session):
    """Test avec un mauvais mot de passe."""
    from schemas import UserCreate
    from core.password import get_password_hash
    from repositories.user_repository import UserRepository
    
    user = UserCreate(
        username="logintest2",
        email="login2@example.com",
        password="password123"
    )
    user_repository = UserRepository(db_session)
    await user_repository.create_user(user)
    
    # Tenter de se connecter avec mauvais mot de passe
    response = await client.post(
        "/auth/token",
        data={
            "username": "logintest2",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    from schemas import UserCreate
    from repositories.user_repository import UserRepository
    """Test avec un utilisateur inexistant."""
    user = UserCreate(
        username="nonexistent",
        email="nonexistent@example.com",
        password="password123"
    )
    
    response = await client.post(
        "/auth/token",
        data={
            "username": "nonexistent",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_inactive_user(client, db_session):
    """Test avec un utilisateur inactif."""
    from schemas import UserCreate, UserUpdate
    from repositories.user_repository import UserRepository
    from core.password import get_password_hash
    
    user_form = UserCreate(
        username="inactive",
        email="inactive@example.com",
        password="password123",
    )
    user_repository = UserRepository(db_session)
    user = await user_repository.create_user(user_form)
    # update the user to inactive
    user_data = UserUpdate(
        is_active=False
    )
    await user_repository.update_user(user.id, user_data)
    
    # Tenter de se connecter avec utilisateur inactif
    response = await client.post(
        "/auth/token",
        data={
            "username": "inactive",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 401
    assert "Inactive user" in response.json()["detail"]

