"""
Helpers pour les tests API.
"""
from httpx import AsyncClient

from app.models import User
from app.schemas import UserCreate

from app.services.auth import AuthenticationService


async def create_user_and_get_token(
    client: AsyncClient,
    auth_service: AuthenticationService,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "password123",
) -> tuple[User, str]:
    """Crée un utilisateur actif et retourne l'utilisateur et son token d'accès."""
    user = await auth_service.register_user(
        UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=password,
        )
    )
    user.is_active = True
    await auth_service.user_repository.update_user(user.id, user)
    
    # Obtenir le token
    from tests.api.authentication.helpers import get_login_url
    response = await client.post(
        get_login_url(),
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return user, token


def get_auth_headers(token: str) -> dict:
    """Retourne les headers d'authentification."""
    return {"Authorization": f"Bearer {token}"}

