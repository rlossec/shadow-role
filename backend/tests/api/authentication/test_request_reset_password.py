
import pytest

from schemas import UserCreate


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
async def test_request_reset_password_generates_token(client, auth_service):
    await create_user(auth_service, "forgot_user", "forgot@example.com", "forgotpass123")

    response = await client.post(
        "/auth/request-reset-password",
        json={"email": "forgot@example.com"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["reset_token"]
    assert data["user_id"]
