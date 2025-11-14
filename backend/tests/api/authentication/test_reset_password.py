"""
Tests pour l'endpoint POST /auth/reset-password.

Pour exécuter ces tests:
    uv run pytest tests/api/authentication/test_reset_password.py -v
    uv run pytest tests/api/authentication/test_reset_password.py::test_reset_password_success -v
"""
import pytest

from tests.api.authentication.helpers import (
    get_base_password_reset_request_payload,
    get_base_password_reset_confirm_payload,
    get_base_login_form_data,
    get_base_login_headers,
    create_inactive_user,
    RESET_PASSWORD_BAD_TOKEN,
)


# 204 - No Content (Success)
@pytest.mark.asyncio
async def test_reset_password_success(client, auth_service):
    """Test réinitialisation de mot de passe avec succès."""
    user = await create_inactive_user(auth_service, "reset_user", "reset@example.com", "oldpassword123")
    await auth_service.set_user_active(user.id, True)
    
    # Demander la réinitialisation
    request_payload = get_base_password_reset_request_payload("reset@example.com")
    forgot_response = await client.post("/auth/request-reset-password", json=request_payload)
    assert forgot_response.status_code == 202
    reset_data = forgot_response.json()
    reset_token = reset_data.get("reset_token")
    assert reset_token
    
    # Réinitialiser le mot de passe
    reset_payload = get_base_password_reset_confirm_payload(
        reset_data.get("user_id"),
        reset_token,
        "newpassword456"
    )
    reset_response = await client.post("/auth/reset-password", json=reset_payload)
    
    assert reset_response.status_code in {200, 204}
    
    # Vérifier que le nouveau mot de passe fonctionne
    login_response = await client.post(
        "/auth/jwt/login",
        data=get_base_login_form_data(username="reset_user", password="newpassword456"),
        headers=get_base_login_headers()
    )
    assert login_response.status_code == 200


# 400 - Bad Request
@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    """Test réinitialisation avec un token invalide."""
    payload = get_base_password_reset_confirm_payload(
        "00000000-0000-0000-0000-000000000000",
        "token-invalide",
        "whatever123"
    )
    response = await client.post("/auth/reset-password", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == RESET_PASSWORD_BAD_TOKEN
