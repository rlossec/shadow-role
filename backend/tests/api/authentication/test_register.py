"""
Tests for the /auth/register endpoint.

To run specific tests:
    uv run pytest tests/api/authentication/test_register.py::test_register_success
    uv run pytest tests/api/authentication/test_register.py -v
"""

import pytest

from db.schemas import UserCreate


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "confirm_password": "testpassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_username(client, auth_service):
    await auth_service.register_user(
        UserCreate(
            username="duplicate",
            email="first@example.com",
            password="password123",
            confirm_password="password123",
        )
    )

    response = await client.post(
        "/auth/register",
        json={
            "username": "duplicate",
            "email": "second@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_register_duplicate_email(client, auth_service):
    await auth_service.register_user(
        UserCreate(
            username="user1",
            email="duplicate@example.com",
            password="password123",
            confirm_password="password123",
        )
    )

    response = await client.post(
        "/auth/register",
        json={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("email" in str(error).lower() for error in errors)


@pytest.mark.asyncio
async def test_register_missing_fields(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "confirm_password": "password123",
        },
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_empty_fields(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "",
            "confirm_password": "",
        },
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_passwords_do_not_match(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "different_password",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("password" in str(error).lower() and "match" in str(error).lower() for error in errors)


@pytest.mark.asyncio
async def test_register_passwords_match(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_passwords_match_case_sensitive(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("password" in str(error).lower() and "match" in str(error).lower() for error in errors)
