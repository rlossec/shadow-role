from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import RevokedRefreshToken


class TokenRepository:
    """Persistence layer for refresh token denylist and related helpers."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def is_refresh_token_revoked(self, jti: str) -> bool:
        result = await self.db.execute(
            select(RevokedRefreshToken).where(RevokedRefreshToken.jti == jti)
        )
        return result.scalar_one_or_none() is not None

    async def get_revoked_refresh_token(self, jti: str) -> Optional[RevokedRefreshToken]:
        result = await self.db.execute(
            select(RevokedRefreshToken).where(RevokedRefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(
        self,
        *,
        jti: str,
        user_id: UUID,
        expires_at: datetime,
        reason: Optional[str] = None,
    ) -> RevokedRefreshToken:
        revoked = await self.get_revoked_refresh_token(jti)
        now = datetime.now(timezone.utc)

        if revoked is None:
            revoked = RevokedRefreshToken(
                jti=jti,
                user_id=user_id,
                expires_at=expires_at,
                revoked_at=now,
                reason=reason,
            )
            self.db.add(revoked)
        else:
            revoked.user_id = user_id
            revoked.expires_at = expires_at
            revoked.revoked_at = now
            revoked.reason = reason or revoked.reason

        await self.db.commit()
        await self.db.refresh(revoked)
        return revoked

