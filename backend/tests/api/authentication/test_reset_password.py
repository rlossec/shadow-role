
import pytest

from schemas import UserCreate
from api.authentication import RESET_PASSWORD_BAD_TOKEN

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
async def test_reset_password_success(client, auth_service):
    user = await create_user(auth_service, "reset_user", "reset@example.com", "oldpassword123")
    await auth_service.set_user_active(user.id, True)

    forgot_response = await client.post(
        "/auth/request-reset-password",
        json={"email": "reset@example.com"},
    )
    assert forgot_response.status_code == 202
    reset_token = forgot_response.json().get("reset_token")
    assert reset_token

    reset_response = await client.post(
        "/auth/reset-password",
        json={
            "user_id": forgot_response.json().get("user_id"),
            "token": reset_token,
            "password": "newpassword456",
        },
    )

    assert reset_response.status_code in {200, 204}

    login_response = await client.post(
        "/auth/jwt/login",
        data={"username": "reset_user", "password": "newpassword456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    response = await client.post(
        "/auth/reset-password",
        json={
            "user_id": "00000000-0000-0000-0000-000000000000",
            "token": "token-invalide",
            "password": "whatever123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == RESET_PASSWORD_BAD_TOKEN
