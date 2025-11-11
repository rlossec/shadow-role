from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import uuid

import jwt
from fastapi import HTTPException, status

from core.config import settings


class JWTRepository:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        refresh_secret_key: Optional[str] = None,
    ) -> None:
        self.secret_key = secret_key
        self.refresh_secret_key = refresh_secret_key or secret_key
        self.algorithm = algorithm

    def _create_token(
        self,
        user_id: uuid.UUID,
        token_type: str,
        expires_delta: timedelta,
        secret_key: str,
    ) -> str:
        now = datetime.now(timezone.utc)
        expire = now + expires_delta
        to_encode = {
            "sub": str(user_id),
            "iat": now,
            "type": token_type,
            "exp": expire,
            "jti": secrets.token_urlsafe(8),
        }
        return jwt.encode(to_encode, secret_key, algorithm=self.algorithm)

    def create_access_token(
        self,
        user_id: uuid.UUID,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return self._create_token(user_id, "access", delta, self.secret_key)

    def create_refresh_token(
        self,
        user_id: uuid.UUID,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        delta = expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        return self._create_token(user_id, "refresh", delta, self.refresh_secret_key)

    def decode_token(self, token: str, secret_key: Optional[str] = None) -> dict:
        try:
            return jwt.decode(token, secret_key or self.secret_key, algorithms=[self.algorithm])
        except (jwt.ExpiredSignatureError, jwt.PyJWTError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré",
            ) from exc

    def decode_refresh_token(self, token: str) -> dict:
        payload = self.decode_token(token, self.refresh_secret_key)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide (pas un refresh token)",
            )
        return payload

    def extract_user_id_from_refresh_token(self, token: str) -> uuid.UUID:
        payload = self.decode_refresh_token(token)
        try:
            return uuid.UUID(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide (sub)",
            ) from exc