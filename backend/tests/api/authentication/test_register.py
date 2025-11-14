"""
Tests pour l'endpoint POST /auth/register.

Pour exécuter ces tests:
    uv run pytest tests/api/authentication/test_register.py -v
    uv run pytest tests/api/authentication/test_register.py::test_register_success -v
"""
import pytest

from schemas import UserCreate
from tests.api.authentication.helpers import (
    get_base_register_payload,
    REGISTER_REQUIRED_FIELDS,
    REGISTER_DUPLICATE_USERNAME,
    REGISTER_DUPLICATE_EMAIL,
)


# 201 - Success
@pytest.mark.asyncio
async def test_register_success(client):
    """Test enregistrement d'un utilisateur avec succès."""
    payload = get_base_register_payload()
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["is_active"] is False  # Inactif par défaut


@pytest.mark.asyncio
async def test_register_passwords_match(client):
    """Test enregistrement avec mots de passe correspondants."""
    payload = get_base_register_payload(
        password="password123",
        confirm_password="password123"
    )
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]


# 422 - Unprocessable Entity (champs obligatoires manquants)
@pytest.mark.asyncio
@pytest.mark.parametrize("missing_field", REGISTER_REQUIRED_FIELDS)
async def test_register_missing_required_fields(client, missing_field):
    """
    Test enregistrement avec un champ obligatoire manquant.
    
    Ce test itère automatiquement sur tous les champs obligatoires
    pour s'assurer que chacun génère une erreur appropriée.
    """
    payload = get_base_register_payload()
    del payload[missing_field]  # Enlever le champ obligatoire
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Vérifier que l'erreur mentionne le champ manquant
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    assert missing_field in error_fields


@pytest.mark.asyncio
async def test_register_missing_all_required_fields(client):
    """Test enregistrement sans aucun champ obligatoire."""
    response = await client.post("/auth/register", json={})
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    error_fields = [err["loc"][-1] for err in errors if isinstance(err, dict) and "loc" in err]
    # Tous les champs obligatoires doivent être présents dans les erreurs
    for required_field in REGISTER_REQUIRED_FIELDS:
        assert required_field in error_fields


# 422 - Unprocessable Entity (validation)
@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Test enregistrement avec un email invalide."""
    payload = get_base_register_payload(email="invalid-email")
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("email" in str(error).lower() for error in errors)


@pytest.mark.asyncio
async def test_register_empty_fields(client):
    """Test enregistrement avec des champs vides."""
    # Username vide
    payload = get_base_register_payload(username="")
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422
    
    # Email vide
    payload = get_base_register_payload(email="")
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422
    
    # Password vide
    payload = get_base_register_payload(password="", confirm_password="")
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422
    
    # Confirm_password vide
    payload = get_base_register_payload(confirm_password="")
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_passwords_do_not_match(client):
    """Test enregistrement avec mots de passe différents."""
    payload = get_base_register_payload(
        password="password123",
        confirm_password="different_password"
    )
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("password" in str(error).lower() and "match" in str(error).lower() for error in errors)


@pytest.mark.asyncio
async def test_register_passwords_match_case_sensitive(client):
    """Test que les mots de passe sont sensibles à la casse."""
    payload = get_base_register_payload(
        password="Password123",
        confirm_password="password123"
    )
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("password" in str(error).lower() and "match" in str(error).lower() for error in errors)


# 400 - Bad Request (doublons)
@pytest.mark.asyncio
async def test_register_duplicate_username(client, auth_service):
    """Test enregistrement avec un username déjà existant."""
    await auth_service.register_user(
        UserCreate(
            username="duplicate",
            email="first@example.com",
            password="password123",
            confirm_password="password123",
        )
    )
    
    payload = get_base_register_payload(
        username="duplicate",
        email="second@example.com"
    )
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == REGISTER_DUPLICATE_USERNAME


@pytest.mark.asyncio
async def test_register_duplicate_email(client, auth_service):
    """Test enregistrement avec un email déjà existant."""
    await auth_service.register_user(
        UserCreate(
            username="user1",
            email="duplicate@example.com",
            password="password123",
            confirm_password="password123",
        )
    )
    
    payload = get_base_register_payload(
        username="user2",
        email="duplicate@example.com"
    )
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == REGISTER_DUPLICATE_EMAIL
