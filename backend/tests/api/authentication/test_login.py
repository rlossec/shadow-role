"""Tests for the /auth/jwt/login endpoint."""

import pytest
from sqlalchemy import select

from db.schemas import UserCreate
from models import User


async def create_user(auth_service, username: str, email: str, password: str) -> User:
    return await auth_service.register_user(
        UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=password,
        )
    )


@pytest.mark.asyncio
async def test_login_success_with_username(client, auth_service):
    await create_user(auth_service, "logintest", "login@example.com", "password123")

    response = await client.post(
        "/auth/jwt/login",
        data={"username": "logintest", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_login_success_with_email(client, auth_service):
    await create_user(auth_service, "logintest2", "login2@example.com", "password123")

    response = await client.post(
        "/auth/jwt/login",
        data={"username": "login2@example.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, auth_service):
    await create_user(auth_service, "logintest3", "login3@example.com", "password123")

    response = await client.post(
        "/auth/jwt/login",
        data={"username": "logintest3", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert "LOGIN_BAD_CREDENTIALS" in error_detail or "invalid" in error_detail.lower() or "incorrect" in error_detail.lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post(
        "/auth/jwt/login",
        data={"username": "nonexistent", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert "LOGIN_BAD_CREDENTIALS" in error_detail or "invalid" in error_detail.lower() or "incorrect" in error_detail.lower()


@pytest.mark.asyncio
async def test_login_nonexistent_email(client):
    response = await client.post(
        "/auth/jwt/login",
        data={"username": "nonexistent@example.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert "LOGIN_BAD_CREDENTIALS" in error_detail or "invalid" in error_detail.lower() or "incorrect" in error_detail.lower()


@pytest.mark.asyncio
async def test_login_inactive_user(client, auth_service, db_session):
    user = await create_user(auth_service, "inactive", "inactive@example.com", "password123")

    result = await db_session.execute(select(User).where(User.id == user.id))
    db_user = result.scalar_one()
    db_user.is_active = False
    await db_session.commit()
    await db_session.refresh(db_user)

    response = await client.post(
        "/auth/jwt/login",
        data={"username": "inactive", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code in (400, 401)
    error_detail = response.json()["detail"]
    assert "inactive" in error_detail.lower() or "LOGIN_BAD_CREDENTIALS" in error_detail


@pytest.mark.asyncio
async def test_login_missing_credentials(client):
    response = await client.post(
        "/auth/jwt/login",
        data={"username": "testuser"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/jwt/login",
        data={"password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_empty_credentials(client):
    response = await client.post(
        "/auth/jwt/login",
        data={"username": "", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400

    response = await client.post(
        "/auth/jwt/login",
        data={"username": "testuser", "password": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_username_vs_email_same_value(client, auth_service):
    await create_user(auth_service, "samevalue", "samevalue@example.com", "password123")

    response1 = await client.post(
        "/auth/jwt/login",
        data={"username": "samevalue", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response1.status_code == 200

    response2 = await client.post(
        "/auth/jwt/login",
        data={"username": "samevalue@example.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response2.status_code == 200
