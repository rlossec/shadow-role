import jwt
import pytest

from core.config import settings
from db.schemas import UserCreate


async def create_user(auth_service, username: str, email: str, password: str):
    return await auth_service.register_user(
        UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=password,
        )
    )


@pytest.mark.asyncio
async def test_refresh_success(client, auth_service):
    user = await create_user(auth_service, "refresh_user", "refresh@example.com", "refreshpass123")

    login_response = await client.post(
        "/auth/jwt/login",
        data={"username": "refresh_user", "password": "refreshpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    refresh_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert new_tokens["token_type"] == "bearer"
    assert new_tokens["access_token"]
    assert new_tokens["access_token"] != tokens["access_token"]

    access_payload = jwt.decode(
        new_tokens["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert access_payload["sub"] == str(user.id)


@pytest.mark.asyncio
async def test_refresh_with_invalid_token_returns_401(client):
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalide ou expiré"


@pytest.mark.asyncio
async def test_refresh_with_access_token_returns_401(client, auth_service):
    await create_user(auth_service, "refresh_user2", "refresh2@example.com", "refreshpass123")

    login_response = await client.post(
        "/auth/jwt/login",
        data={"username": "refresh_user2", "password": "refreshpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalide (pas un refresh token)"
