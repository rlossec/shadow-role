"""
Tests pour l'endpoint POST /auth/activate-account.

Pour exécuter ces tests:
    uv run pytest tests/api/authentication/test_activate_account.py -v
    uv run pytest tests/api/authentication/test_activate_account.py::test_activate_account_user_success -v
"""
import pytest
from sqlalchemy import select

from models.user import User
from tests.api.authentication.helpers import (
    get_base_account_activation_confirm_payload,
    create_inactive_user,
    ACCOUNT_ACTIVATION_BAD_TOKEN,
)


# 200 - Success
@pytest.mark.asyncio
async def test_activate_account_user_success(
    client,
    auth_service,
    account_activation_manager,
    db_session,
    notification_service,
):
    """Test activation de compte avec succès."""
    user = await create_inactive_user(
        auth_service,
        "inactive_activate_user",
        "inactive_activate@example.com",
        "activatepass123",
    )
    
    activation_token = await account_activation_manager.create_token(user)
    
    payload = get_base_account_activation_confirm_payload(str(user.id), activation_token)
    activation_response = await client.post("/auth/activate-account", json=payload)
    
    assert activation_response.status_code == 200
    data = activation_response.json()
    assert data["is_active"] is True
    
    # Vérifier en base de données
    result = await db_session.execute(select(User).where(User.email == "inactive_activate@example.com"))
    refreshed_user = result.scalar_one()
    assert refreshed_user.is_active is True
    
    # Vérifier que la notification a été envoyée
    assert notification_service.calls == [
        {
            "to": user.email,
            "template": "auth_activation_confirmation",
            "context": {"username": user.username},
        }
    ]


# 400 - Bad Request
@pytest.mark.asyncio
async def test_activate_account_with_bad_token_returns_400(client):
    """Test activation avec un token invalide."""
    payload = get_base_account_activation_confirm_payload(
        "00000000-0000-0000-0000-000000000000",
        "mauvais-token"
    )
    response = await client.post("/auth/activate-account", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == ACCOUNT_ACTIVATION_BAD_TOKEN
