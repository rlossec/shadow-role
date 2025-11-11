"""Auth service package with cohesive components."""

from .service import AuthenticationService
from .token_manager import PasswordResetManager, AccountActivationTokenManager
from .dependencies import (
    get_authentication_service,
    get_password_reset_manager,
    get_account_activation_manager,
    get_current_user,
    get_current_active_user,
)
from .link_builder import NotificationLinkBuilder

__all__ = [
    "AuthenticationService",
    "PasswordResetManager",
    "AccountActivationTokenManager",
    "NotificationLinkBuilder",
    "get_authentication_service",
    "get_password_reset_manager",
    "get_account_activation_manager",
    "get_current_user",
    "get_current_active_user",
]
