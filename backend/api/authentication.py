from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from schemas import (
    TokenPair,
    UserCreate,
    UserResponse,
    PasswordResetEmailRequest,
    PasswordResetConfirmRequest,
    AccountActivationRequest,
    AccountActivationConfirmRequest,
    RefreshRequest,
    PasswordResetResponse,
    AccountActivationResponse,
)
from services.auth import (
    AuthenticationService,
    PasswordResetManager,
    AccountActivationTokenManager,
    get_authentication_service,
    get_password_reset_manager,
    get_account_activation_manager,
    get_current_active_user,
)

# Error messages
LOGIN_BAD_CREDENTIALS = "Credentials are incorrect"
INVALID_REFRESH_TOKEN = "Invalid refresh token"
RESET_PASSWORD_BAD_TOKEN = "Reset password token is invalid"
ACCOUNT_ACTIVATION_BAD_TOKEN = "Account activation token is invalid"
REGISTER_DUPLICATE_USERNAME = "Username already exists"
REGISTER_DUPLICATE_EMAIL = "Email already exists"
REGISTER_INVALID_EMAIL = "Invalid email"
REGISTER_MISSING_FIELDS = "Missing fields"
REGISTER_EMPTY_FIELDS = "Empty fields"
REGISTER_WEAK_PASSWORD = "Weak password"
REGISTER_SPECIAL_CHARACTERS_IN_USERNAME = "Special characters are not allowed in username"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    account_activation_manager: AccountActivationTokenManager = Depends(get_account_activation_manager),
):
    user = await auth_service.register_user(payload)
    activation_token = await account_activation_manager.create_token(user)
    await auth_service.notify_account_activation(user, activation_token)
    return UserResponse.model_validate(user)


@router.post("/jwt/login", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends(get_authentication_service),
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=LOGIN_BAD_CREDENTIALS)

    access_token, refresh_token = auth_service.create_token_pair(user.id)
    return TokenPair(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    payload: RefreshRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
):
    access_token, refresh_token = await auth_service.rotate_refresh_token(payload.refresh_token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/jwt/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
):
    await auth_service.revoke_refresh_token(payload.refresh_token, reason="logout")
    return None


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: UserResponse = Depends(get_current_active_user),
) -> UserResponse:
    return current_user


@router.post(
    "/request-reset-password",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PasswordResetResponse,
)
async def request_reset_password(
    payload: PasswordResetEmailRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    reset_manager: PasswordResetManager = Depends(get_password_reset_manager),
):
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        return PasswordResetResponse(reset_token=None, user_id=None)

    token = await reset_manager.create_token(user)
    await auth_service.notify_password_reset(user, token)
    return PasswordResetResponse(reset_token=token, user_id=user.id)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    payload: PasswordResetConfirmRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    reset_manager: PasswordResetManager = Depends(get_password_reset_manager),
):
    reset_token = await reset_manager.verify_token(payload.token)
    if not reset_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RESET_PASSWORD_BAD_TOKEN)

    if str(reset_token.user_id) != str(payload.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RESET_PASSWORD_BAD_TOKEN)

    await auth_service.set_user_password(reset_token.user_id, payload.password)
    await reset_manager.mark_token_used(reset_token)
    return None


@router.post(
    "/resend_activation",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AccountActivationResponse,
)
async def resend_activation(
    payload: AccountActivationRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    account_activation_manager: AccountActivationTokenManager = Depends(get_account_activation_manager),
):
    user = await auth_service.get_user_by_email(payload.email)
    if not user or user.is_active:
        return AccountActivationResponse(activation_token=None, user_id=None)

    token = await account_activation_manager.create_token(user)
    await auth_service.notify_account_activation(user, token)
    return AccountActivationResponse(activation_token=token, user_id=user.id)


@router.post("/activate-account", response_model=UserResponse)
async def activate_account(
    payload: AccountActivationConfirmRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    account_activation_manager: AccountActivationTokenManager = Depends(get_account_activation_manager),
):
    account_activation_token = await account_activation_manager.verify_token(payload.token)
    if not account_activation_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ACCOUNT_ACTIVATION_BAD_TOKEN)

    if str(account_activation_token.user_id) != str(payload.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ACCOUNT_ACTIVATION_BAD_TOKEN)

    await auth_service.set_user_active(account_activation_token.user_id, True)
    await account_activation_manager.mark_token_used(account_activation_token)

    user = await auth_service.get_user_by_id(account_activation_token.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ACCOUNT_ACTIVATION_BAD_TOKEN)

    await auth_service.notify_activation_confirmation(user)

    return UserResponse.model_validate(user)
