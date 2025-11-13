from uuid import UUID

from pydantic import BaseModel, EmailStr


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenPair(AccessToken):
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None



class PasswordResetEmailRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    user_id: UUID
    token: str
    password: str


class AccountActivationRequest(BaseModel):
    email: EmailStr


class AccountActivationConfirmRequest(BaseModel):
    user_id: UUID
    token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetResponse(BaseModel):
    user_id: UUID | None = None
    reset_token: str | None = None


class AccountActivationResponse(BaseModel):
    user_id: UUID | None = None
    activation_token: str | None = None