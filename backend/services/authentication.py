"""Backward compatibility wrapper for auth services."""

from services.auth import (
    AuthenticationService,
    PasswordResetManager,
    VerificationTokenManager,
    get_authentication_service,
    get_password_reset_manager,
    get_verification_manager,
    get_current_user,
    get_current_active_user,
)

