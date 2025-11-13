
import pytest

from sqlalchemy import select

from schemas import UserCreate
from models.user import User

from api.authentication import ACCOUNT_ACTIVATION_BAD_TOKEN
async def create_inactive_user(auth_service, username: str, email: str, password: str):
    return await auth_service.register_user(
        UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=password,
        )
    )


@pytest.mark.asyncio
async def test_activate_account_user_success(
    client,
    auth_service,
    account_activation_manager,
    db_session,
    notification_service,
):
    user = await create_inactive_user(
        auth_service,
        "inactive_activate_user",
        "inactive_activate@example.com",
        "activatepass123",
    )

    activation_token = await account_activation_manager.create_token(user)

    activation_response = await client.post(
        "/auth/activate-account",
        json={"user_id": str(user.id), "token": activation_token},
    )

    assert activation_response.status_code == 200
    data = activation_response.json()
    assert data["is_active"] is True

    result = await db_session.execute(select(User).where(User.email == "inactive_activate@example.com"))
    refreshed_user = result.scalar_one()
    assert refreshed_user.is_active is True
    assert notification_service.calls == [
        {
            "to": user.email,
            "template": "auth_activation_confirmation",
            "context": {"username": user.username},
        }
    ]


@pytest.mark.asyncio
async def test_activate_account_with_bad_token_returns_400(client):
    response = await client.post(
        "/auth/activate-account",
        json={"user_id": "00000000-0000-0000-0000-000000000000", "token": "mauvais-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ACCOUNT_ACTIVATION_BAD_TOKEN
