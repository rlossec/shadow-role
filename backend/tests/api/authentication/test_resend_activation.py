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
async def test_resend_activation_success(client, auth_service):
    await create_user(auth_service, "activate_user", "activate@example.com", "activatepass123")

    response = await client.post(
        "/auth/resend_activation",
        json={"email": "activate@example.com"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["activation_token"]
    assert data["user_id"]


@pytest.mark.asyncio
async def test_resend_activation_unknown_email_returns_no_token(client):
    response = await client.post(
        "/auth/resend_activation",
        json={"email": "unknown@example.com"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["activation_token"] is None
    assert data["user_id"] is None


@pytest.mark.asyncio
async def test_resend_activation_user_already_active_returns_no_token(client, auth_service):
    user = await create_user(auth_service, "already_active", "already_active@example.com", "activatepass123")
    await auth_service.set_user_active(user.id, True)

    response = await client.post(
        "/auth/resend_activation",
        json={"email": "already_active@example.com"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["activation_token"] is None
    assert data["user_id"] is None

