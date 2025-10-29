"""
Tests for the /auth/refresh endpoint.

short cut command to run the test:
uv run pytest tests/test_auth_refresh.py::test_refresh_success
uv run pytest tests/test_auth_refresh.py::test_refresh_with_expired_token
uv run pytest tests/test_auth_refresh.py::test_refresh_with_invalid_token
uv run pytest tests/test_auth_refresh.py::test_refresh_with_nonexistent_user
uv run pytest tests/test_auth_refresh.py::test_refresh_with_inactive_user
"""

import pytest
from datetime import timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, db_session):
    """Test successful token refresh with valid token."""
    import asyncio
    from schemas import UserCreate
    from repositories.user_repository import UserRepository
    from core.security import create_access_token
    
    user_form = UserCreate(
        username="refreshtest",
        email="refresh@example.com",
        password="password123"
    )
    user_repository = UserRepository(db_session)
    user = await user_repository.create_user(user_form)
    
    token = create_access_token(data={"sub": str(user.id)})
    
    # Wait a bit to ensure the new token will have a different expiration
    await asyncio.sleep(0.1)
    
    response = await client.post(
        "/auth/refresh",
        data={"refresh_token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    
    # Verify that the new token works correctly
    new_token = data["access_token"]
    assert len(new_token) > 0
    
    # The new token should allow access to /auth/me
    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {new_token}"}
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == "refreshtest"
    assert me_data["email"] == "refresh@example.com"


@pytest.mark.asyncio
async def test_refresh_with_expired_token(client: AsyncClient, db_session):
    """Test refresh with an expired token (should still work)."""
    from schemas import UserCreate
    from repositories.user_repository import UserRepository
    from core.security import create_access_token

    user_form = UserCreate(
        username="refreshexpired",
        email="refreshexpired@example.com",
        password="password123"
    )
    user_repository = UserRepository(db_session)
    user = await user_repository.create_user(user_form)
    
    expired_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(seconds=-1)
    )
    
    response = await client.post(
        "/auth/refresh",
        data={"refresh_token": expired_token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient):
    """Test refresh with an invalid token."""
    response = await client.post(
        "/auth/refresh",
        data={"refresh_token": "invalid_token_12345"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_with_nonexistent_user(client: AsyncClient, db_session):
    """Test refresh with token for non-existent user."""
    from core.security import create_access_token

    fake_token = create_access_token(data={"sub": "99999"})
    
    response = await client.post(
        "/auth/refresh",
        data={"refresh_token": fake_token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_with_inactive_user(client: AsyncClient, db_session):
    """Test refresh with inactive user token."""
    from schemas import UserCreate, UserUpdate
    from repositories.user_repository import UserRepository
    from core.security import create_access_token
    
    user_form = UserCreate(
        username="refreshinactive",
        email="refreshinactive@example.com",
        password="password123"
    )
    user_repository = UserRepository(db_session)
    user = await user_repository.create_user(user_form)
    
    token = create_access_token(data={"sub": str(user.id)})
    
    user_data = UserUpdate(is_active=False)
    await user_repository.update_user(user.id, user_data)
    
    response = await client.post(
        "/auth/refresh",
        data={"refresh_token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert "Inactive user" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_missing_token(client: AsyncClient):
    """Test refresh without providing token."""
    response = await client.post(
        "/auth/refresh",
        data={},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 422

