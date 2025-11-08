"""Auth service package with cohesive components."""

from .service import AuthenticationService
from .token_manager import PasswordResetManager, VerificationTokenManager
from .dependencies import (
    get_authentication_service,
    get_password_reset_manager,
    get_verification_manager,
    get_current_user,
    get_current_active_user,
)

__all__ = [
    "AuthenticationService",
    "PasswordResetManager",
    "VerificationTokenManager",
    "get_authentication_service",
    "get_password_reset_manager",
    "get_verification_manager",
    "get_current_user",
    "get_current_active_user",
]
