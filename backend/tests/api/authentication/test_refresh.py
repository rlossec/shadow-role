import jwt
import pytest

from core.config import settings
from schemas import UserCreate


async def create_user(auth_service, username: str, email: str, password: str):
    user = await auth_service.register_user(
        UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=password,
        )
    )
    user.is_active = True
    await auth_service.user_repository.update_user(user.id, user)
    return user


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
    assert new_tokens["refresh_token"]
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    access_payload = jwt.decode(
        new_tokens["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert access_payload["sub"] == str(user.id)

    # Vérifie que le nouveau refresh token permet une nouvelle rotation
    second_refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert second_refresh.status_code == 200
    rotated_tokens = second_refresh.json()
    assert rotated_tokens["access_token"] != new_tokens["access_token"]
    assert rotated_tokens["refresh_token"] != new_tokens["refresh_token"]


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


@pytest.mark.asyncio
async def test_reusing_refresh_token_fails(client, auth_service):
    await create_user(auth_service, "refresh_user3", "refresh3@example.com", "refreshpass123")

    login_response = await client.post(
        "/auth/jwt/login",
        data={"username": "refresh_user3", "password": "refreshpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    first_refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert first_refresh.status_code == 200

    reuse_attempt = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reuse_attempt.status_code == 401
    assert reuse_attempt.json()["detail"] == "Refresh token révoqué"


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client, auth_service):
    await create_user(auth_service, "logout_user", "logout@example.com", "logoutpass123")

    login_response = await client.post(
        "/auth/jwt/login",
        data={"username": "logout_user", "password": "logoutpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    logout_response = await client.post(
        "/auth/jwt/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert logout_response.status_code == 204

    refresh_after_logout = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_after_logout.status_code == 401
    assert refresh_after_logout.json()["detail"] == "Refresh token révoqué"
