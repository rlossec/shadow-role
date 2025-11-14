"""
Tests pour l'endpoint POST /auth/refresh.

Pour exécuter ces tests:
    uv run pytest tests/api/authentication/test_refresh.py -v
    uv run pytest tests/api/authentication/test_refresh.py::test_refresh_success -v
"""
import jwt
import pytest

from core.config import settings
from tests.api.authentication.helpers import (
    get_base_login_form_data,
    get_base_login_headers,
    get_base_refresh_payload,
    create_active_user,
)


# 200 - Success
@pytest.mark.asyncio
async def test_refresh_success(client, auth_service):
    """Test rafraîchissement de token avec succès."""
    user = await create_active_user(auth_service, "refresh_user", "refresh@example.com", "refreshpass123")
    
    # Login pour obtenir les tokens
    login_response = await client.post(
        "/auth/jwt/login",
        data=get_base_login_form_data(username="refresh_user", password="refreshpass123"),
        headers=get_base_login_headers()
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    # Rafraîchir les tokens
    refresh_payload = get_base_refresh_payload(tokens["refresh_token"])
    refresh_response = await client.post("/auth/refresh", json=refresh_payload)
    
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert new_tokens["token_type"] == "bearer"
    assert new_tokens["access_token"]
    assert new_tokens["refresh_token"]
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]
    
    # Vérifier que le nouveau access token est valide
    access_payload = jwt.decode(
        new_tokens["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert access_payload["sub"] == str(user.id)
    
    # Vérifier que le nouveau refresh token permet une nouvelle rotation
    second_refresh = await client.post(
        "/auth/refresh",
        json=get_base_refresh_payload(new_tokens["refresh_token"])
    )
    assert second_refresh.status_code == 200
    rotated_tokens = second_refresh.json()
    assert rotated_tokens["access_token"] != new_tokens["access_token"]
    assert rotated_tokens["refresh_token"] != new_tokens["refresh_token"]


@pytest.mark.asyncio
async def test_reusing_refresh_token_fails(client, auth_service):
    """Test qu'un refresh token révoqué ne peut plus être utilisé."""
    await create_active_user(auth_service, "refresh_user3", "refresh3@example.com", "refreshpass123")
    
    # Login pour obtenir les tokens
    login_response = await client.post(
        "/auth/jwt/login",
        data=get_base_login_form_data(username="refresh_user3", password="refreshpass123"),
        headers=get_base_login_headers()
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    # Premier refresh
    first_refresh = await client.post(
        "/auth/refresh",
        json=get_base_refresh_payload(tokens["refresh_token"])
    )
    assert first_refresh.status_code == 200
    
    # Tentative de réutilisation du même refresh token (doit échouer)
    reuse_attempt = await client.post(
        "/auth/refresh",
        json=get_base_refresh_payload(tokens["refresh_token"])
    )
    assert reuse_attempt.status_code == 401
    assert reuse_attempt.json()["detail"] == "Refresh token révoqué"


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client, auth_service):
    """Test que le logout révoque le refresh token."""
    await create_active_user(auth_service, "logout_user", "logout@example.com", "logoutpass123")
    
    # Login pour obtenir les tokens
    login_response = await client.post(
        "/auth/jwt/login",
        data=get_base_login_form_data(username="logout_user", password="logoutpass123"),
        headers=get_base_login_headers()
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    # Logout (révoque le refresh token)
    logout_response = await client.post(
        "/auth/jwt/logout",
        json=get_base_refresh_payload(tokens["refresh_token"])
    )
    assert logout_response.status_code == 204
    
    # Tentative de refresh après logout (doit échouer)
    refresh_after_logout = await client.post(
        "/auth/refresh",
        json=get_base_refresh_payload(tokens["refresh_token"])
    )
    assert refresh_after_logout.status_code == 401
    assert refresh_after_logout.json()["detail"] == "Refresh token révoqué"


# 401 - Unauthorized
@pytest.mark.asyncio
async def test_refresh_with_invalid_token_returns_401(client):
    """Test rafraîchissement avec un token invalide."""
    refresh_payload = get_base_refresh_payload("invalid-token")
    response = await client.post("/auth/refresh", json=refresh_payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalide ou expiré"


@pytest.mark.asyncio
async def test_refresh_with_access_token_returns_401(client, auth_service):
    """Test que l'utilisation d'un access token comme refresh token est refusée."""
    await create_active_user(auth_service, "refresh_user2", "refresh2@example.com", "refreshpass123")
    
    # Login pour obtenir les tokens
    login_response = await client.post(
        "/auth/jwt/login",
        data=get_base_login_form_data(username="refresh_user2", password="refreshpass123"),
        headers=get_base_login_headers()
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    # Tentative d'utiliser l'access token comme refresh token (doit échouer)
    response = await client.post(
        "/auth/refresh",
        json=get_base_refresh_payload(tokens["access_token"])
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalide (pas un refresh token)"
