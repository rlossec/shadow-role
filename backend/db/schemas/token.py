from pydantic import BaseModel, EmailStr


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenPair(AccessToken):
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None



class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class RequestVerifyToken(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordResponse(BaseModel):
    reset_token: str | None = None


class RequestVerifyTokenResponse(BaseModel):
    verification_token: str | None = None