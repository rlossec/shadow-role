from __future__ import annotations

from uuid import UUID

from urllib.parse import quote

from core.config import settings


class NotificationLinkBuilder:
    """Construit les liens utilisés par le domaine d’authentification."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.FRONTEND_BASE_URL).rstrip("/")

    def build_activation_link(self, user_id: UUID, token: str) -> str:
        return self._build_path("auth", "activate-account", str(user_id), token)

    def build_reset_password_link(self, user_id: UUID, token: str) -> str:
        return self._build_path("auth", "reset-password", str(user_id), token)

    def _build_path(self, *segments: str) -> str:
        normalized_segments = [segment.strip("/") for segment in segments if segment]
        encoded_segments = [
            quote(segment, safe="") if index == len(normalized_segments) - 1 else segment
            for index, segment in enumerate(normalized_segments)
        ]
        path = "/".join(encoded_segments)
        return f"{self.base_url}/{path}"

