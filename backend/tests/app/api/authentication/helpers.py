"""
Helpers pour les tests des endpoints d'authentification.

Contient les payloads de base, constantes et utilitaires réutilisables.
"""
from typing import Dict, Any
from app.schemas import UserCreate
from app.models import User

# Import de l'app FastAPI pour le reverse lookup des URLs
from main import app


# Messages d'erreur de l'API
LOGIN_BAD_CREDENTIALS = "Credentials are incorrect"
RESET_PASSWORD_BAD_TOKEN = "Reset password token is invalid"
ACCOUNT_ACTIVATION_BAD_TOKEN = "Account activation token is invalid"
REGISTER_DUPLICATE_USERNAME = "Username already exists"
REGISTER_DUPLICATE_EMAIL = "Email already exists"


# Fonctions helper pour générer les URLs via FastAPI reverse lookup
def get_register_url() -> str:
    return str(app.url_path_for("register"))


def get_login_url() -> str:
    return str(app.url_path_for("login"))


def get_logout_url() -> str:
    return str(app.url_path_for("logout"))


def get_refresh_url() -> str:
    return str(app.url_path_for("refresh_token"))


def get_activate_account_url() -> str:
    return str(app.url_path_for("activate_account"))


def get_resend_activation_url() -> str:
    return str(app.url_path_for("resend_activation"))


def get_request_reset_password_url() -> str:
    return str(app.url_path_for("request_reset_password"))


def get_reset_password_url() -> str:
    return str(app.url_path_for("reset_password"))


def get_current_user_url() -> str:
    return str(app.url_path_for("get_current_user"))


def get_base_register_payload(
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
    confirm_password: str = None
) -> Dict[str, Any]:
    if confirm_password is None:
        confirm_password = password
    return {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": confirm_password
    }


def get_base_login_form_data(
    username: str = "testuser",
    password: str = "testpassword123"
) -> Dict[str, str]:
    return {
        "username": username,
        "password": password
    }


def get_base_login_headers() -> Dict[str, str]:
    """Retourne les headers pour le login (form-urlencoded)."""
    return {"Content-Type": "application/x-www-form-urlencoded"}


def get_base_refresh_payload(refresh_token: str) -> Dict[str, str]:
    """
    Retourne un payload de base pour rafraîchir un token.
    
    Args:
        refresh_token: Le refresh token
    
    Returns:
        Dict avec refresh_token
    """
    return {"refresh_token": refresh_token}


def get_base_account_activation_request_payload(email: str = "test@example.com") -> Dict[str, str]:
    """
    Retourne un payload de base pour demander l'activation du compte.
    
    Args:
        email: Email de l'utilisateur
    
    Returns:
        Dict avec email
    """
    return {"email": email}


def get_base_account_activation_confirm_payload(user_id: str, token: str) -> Dict[str, str]:
    """
    Retourne un payload de base pour confirmer l'activation du compte.
    
    Args:
        user_id: UUID de l'utilisateur (string)
        token: Token d'activation
    
    Returns:
        Dict avec user_id et token
    """
    return {
        "user_id": user_id,
        "token": token
    }


def get_base_password_reset_request_payload(email: str = "test@example.com") -> Dict[str, str]:
    """
    Retourne un payload de base pour demander la réinitialisation du mot de passe.
    
    Args:
        email: Email de l'utilisateur
    
    Returns:
        Dict avec email
    """
    return {"email": email}


def get_base_password_reset_confirm_payload(
    user_id: str,
    token: str,
    password: str = "newpassword123"
) -> Dict[str, str]:
    """
    Retourne un payload de base pour confirmer la réinitialisation du mot de passe.
    
    Args:
        user_id: UUID de l'utilisateur (string)
        token: Token de réinitialisation
        password: Nouveau mot de passe
    
    Returns:
        Dict avec user_id, token et password
    """
    return {
        "user_id": user_id,
        "token": token,
        "password": password
    }


# Champs obligatoires pour chaque endpoint
REGISTER_REQUIRED_FIELDS = ["username", "email", "password", "confirm_password"]
LOGIN_REQUIRED_FIELDS = ["username", "password"]
REFRESH_REQUIRED_FIELDS = ["refresh_token"]
ACCOUNT_ACTIVATION_REQUEST_REQUIRED_FIELDS = ["email"]
ACCOUNT_ACTIVATION_CONFIRM_REQUIRED_FIELDS = ["user_id", "token"]
PASSWORD_RESET_REQUEST_REQUIRED_FIELDS = ["email"]
PASSWORD_RESET_CONFIRM_REQUIRED_FIELDS = ["user_id", "token", "password"]


async def create_active_user(auth_service, username: str, email: str, password: str) -> User:
    """
    Helper pour créer un utilisateur actif.
    
    Args:
        auth_service: Service d'authentification
        username: Nom d'utilisateur
        email: Email
        password: Mot de passe
    
    Returns:
        User créé et activé
    """
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
    return user


async def create_inactive_user(auth_service, username: str, email: str, password: str) -> User:
    """
    Helper pour créer un utilisateur inactif.
    
    Args:
        auth_service: Service d'authentification
        username: Nom d'utilisateur
        email: Email
        password: Mot de passe
    
    Returns:
        User créé (inactif par défaut)
    """
    return await auth_service.register_user(
        UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=password,
        )
    )

