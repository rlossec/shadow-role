from __future__ import annotations

from typing import Any, Protocol


class NotificationService(Protocol):
    """Interface générique d’envoi de notifications basée sur des modèles."""

    async def send(self, to: str, template_name: str, context: dict[str, Any]) -> None:
        """Envoyer une notification via un template et un contexte."""
        ...

