from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import (
    create_access_token, 
    authenticate_user, 
    get_current_active_user,
    decode_access_token_optional_expiry
)
from schemas import UserResponse, Token
from core.config import settings
from repositories.user_repository import UserRepository

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint - accepts form-urlencoded (OAuth2 standard)"""
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        # Vérifier si c'est un problème de credentials ou d'utilisateur inactif
        user_repository = UserRepository(db)
        user_check = await user_repository.get_user_by_username(form_data.username)
        if user_check and not user_check.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token - accepts form-urlencoded with refresh_token"""
    # Décoder le token même s'il est expiré (decode_access_token_optional_expiry lève HTTPException si invalide)
    payload = decode_access_token_optional_expiry(refresh_token)
    
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier que l'utilisateur existe toujours et est actif
    user_repository = UserRepository(db)
    user_in_db = await user_repository.get_user(user_id)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user_in_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer un nouveau access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Register endpoint - accepts form-urlencoded with username, email and password"""
    from schemas import UserCreate
    
    user_repository = UserRepository(db)
    existing_user = await user_repository.get_user_by_username(username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    existing_user = await user_repository.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    try:
        user_data = UserCreate(username=username, email=email, password=password)
        new_user = await user_repository.create_user(user_data)
        return UserResponse.model_validate(new_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )