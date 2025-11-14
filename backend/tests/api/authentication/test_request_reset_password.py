"""
Tests pour l'endpoint POST /auth/request-reset-password.

Pour exécuter ces tests:
    uv run pytest tests/api/authentication/test_request_reset_password.py -v
    uv run pytest tests/api/authentication/test_request_reset_password.py::test_request_reset_password_generates_token -v
"""
import pytest

from tests.api.authentication.helpers import (
    get_base_password_reset_request_payload,
    create_inactive_user,
)


# 202 - Accepted
@pytest.mark.asyncio
async def test_request_reset_password_generates_token(client, auth_service):
    """Test demande de réinitialisation génère un token."""
    await create_inactive_user(auth_service, "forgot_user", "forgot@example.com", "forgotpass123")
    
    payload = get_base_password_reset_request_payload("forgot@example.com")
    response = await client.post("/auth/request-reset-password", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert data["reset_token"]
    assert data["user_id"]
