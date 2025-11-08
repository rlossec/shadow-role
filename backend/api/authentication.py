from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from db.schemas import (
    TokenPair,
    AccessToken,
    UserCreate,
    UserResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RequestVerifyToken,
    VerifyRequest,
    RefreshRequest,
    ForgotPasswordResponse,
    RequestVerifyTokenResponse,
)
from services.auth import (
    AuthenticationService,
    PasswordResetManager,
    VerificationTokenManager,
    get_current_active_user,
    get_authentication_service,
    get_password_reset_manager,
    get_verification_manager,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    auth_service: AuthenticationService = Depends(get_authentication_service),
):
    user = await auth_service.register_user(payload)
    return UserResponse.model_validate(user)


@router.post("/jwt/login", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends(get_authentication_service),
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="LOGIN_BAD_CREDENTIALS")

    access_token, refresh_token = auth_service.create_token_pair(user.id)
    return TokenPair(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/jwt/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(_: UserResponse = Depends(get_current_active_user)):
    return None


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(
    payload: RefreshRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
):
    user_id = auth_service.extract_user_id_from_refresh_token(payload.refresh_token)
    user = await auth_service.get_user_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_REFRESH_TOKEN")

    access_token = auth_service.create_access_token(user.id)

    return AccessToken(access_token=access_token, token_type="bearer")


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED, response_model=ForgotPasswordResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    reset_manager: PasswordResetManager = Depends(get_password_reset_manager),
):
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        return ForgotPasswordResponse(reset_token=None)

    token = await reset_manager.create_token(user)
    return ForgotPasswordResponse(reset_token=token)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    reset_manager: PasswordResetManager = Depends(get_password_reset_manager),
):
    reset_token = await reset_manager.verify_token(payload.token)
    if not reset_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RESET_PASSWORD_BAD_TOKEN")

    await auth_service.set_user_password(reset_token.user_id, payload.password)
    await reset_manager.mark_token_used(reset_token)
    return None


@router.post(
    "/request-verify-token",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=RequestVerifyTokenResponse,
)
async def request_verify_token(
    payload: RequestVerifyToken,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    verification_manager: VerificationTokenManager = Depends(get_verification_manager),
):
    user = await auth_service.get_user_by_email(payload.email)
    if not user or not user.is_active or user.is_verified:
        return RequestVerifyTokenResponse(verification_token=None)

    token = await verification_manager.create_token(user)
    return RequestVerifyTokenResponse(verification_token=token)


@router.post("/verify", response_model=UserResponse)
async def verify(
    payload: VerifyRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    verification_manager: VerificationTokenManager = Depends(get_verification_manager),
):
    verification_token = await verification_manager.verify_token(payload.token)
    if not verification_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VERIFY_USER_BAD_TOKEN")

    await auth_service.set_user_verified(verification_token.user_id)
    await verification_manager.mark_token_used(verification_token)

    user = await auth_service.get_user_by_id(verification_token.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VERIFY_USER_BAD_TOKEN")

    return UserResponse.model_validate(user)




