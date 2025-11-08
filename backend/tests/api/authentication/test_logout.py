import pytest

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
async def test_logout_success(client, auth_service):
    await create_user(auth_service, "logout_user", "logout@example.com", "logoutpass123")

    login_response = await client.post(
        "/auth/jwt/login",
        data={"username": "logout_user", "password": "logoutpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    logout_response = await client.post(
        "/auth/jwt/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert logout_response.status_code == 204


@pytest.mark.asyncio
async def test_logout_without_token_returns_401(client):
    response = await client.post("/auth/jwt/logout")
    assert response.status_code == 401








