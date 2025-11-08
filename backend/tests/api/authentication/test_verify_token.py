
import pytest

from sqlalchemy import select

from db.schemas import UserCreate
from models.user import User


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
async def test_request_verify_token_and_verify_success(client, auth_service, db_session):
    await create_user(auth_service, "verify_user", "verify@example.com", "verifypass123")

    request_token_response = await client.post(
        "/auth/request-verify-token",
        json={"email": "verify@example.com"},
    )
    assert request_token_response.status_code == 202
    verify_token = request_token_response.json().get("verification_token")
    assert verify_token

    verify_response = await client.post(
        "/auth/verify",
        json={"token": verify_token},
    )

    assert verify_response.status_code == 200
    data = verify_response.json()
    assert data["is_verified"] is True

    result = await db_session.execute(select(User).where(User.email == "verify@example.com"))
    user = result.scalar_one()
    assert user.is_verified is True


@pytest.mark.asyncio
async def test_verify_with_bad_token_returns_400(client):
    response = await client.post(
        "/auth/verify",
        json={"token": "mauvais-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "VERIFY_USER_BAD_TOKEN"
