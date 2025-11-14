"""
Tests pour l'endpoint POST /auth/resend_activation.

Pour exécuter ces tests:
    uv run pytest tests/api/authentication/test_resend_activation.py -v
    uv run pytest tests/api/authentication/test_resend_activation.py::test_resend_activation_success -v
"""
import pytest

from tests.api.authentication.helpers import (
    get_base_account_activation_request_payload,
    create_inactive_user,
)


# 202 - Accepted
@pytest.mark.asyncio
async def test_resend_activation_success(client, auth_service):
    """Test renvoi d'activation avec succès."""
    await create_inactive_user(auth_service, "activate_user", "activate@example.com", "activatepass123")
    
    payload = get_base_account_activation_request_payload("activate@example.com")
    response = await client.post("/auth/resend_activation", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert data["activation_token"]
    assert data["user_id"]


@pytest.mark.asyncio
async def test_resend_activation_unknown_email_returns_no_token(client):
    """Test renvoi d'activation avec un email inconnu (pas de fuite d'information)."""
    payload = get_base_account_activation_request_payload("unknown@example.com")
    response = await client.post("/auth/resend_activation", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert data["activation_token"] is None
    assert data["user_id"] is None


@pytest.mark.asyncio
async def test_resend_activation_user_already_active_returns_no_token(client, auth_service):
    """Test renvoi d'activation pour un utilisateur déjà actif (aucun token renvoyé)."""
    user = await create_inactive_user(auth_service, "already_active", "already_active@example.com", "activatepass123")
    await auth_service.set_user_active(user.id, True)
    
    payload = get_base_account_activation_request_payload("already_active@example.com")
    response = await client.post("/auth/resend_activation", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert data["activation_token"] is None
    assert data["user_id"] is None
