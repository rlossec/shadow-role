from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from .email_service import EmailNotificationService
from .interface import NotificationService
from .smtp_client import SMTPClient
from .template_manager import NotificationTemplateManager


@lru_cache(maxsize=1)
def get_template_manager() -> NotificationTemplateManager:
    return NotificationTemplateManager()


def get_smtp_client() -> SMTPClient:
    return SMTPClient()


def get_notification_service(
    smtp_client: SMTPClient = Depends(get_smtp_client),
    template_manager: NotificationTemplateManager = Depends(get_template_manager),
) -> NotificationService:
    return EmailNotificationService(
        smtp_client=smtp_client,
        template_manager=template_manager,
    )

