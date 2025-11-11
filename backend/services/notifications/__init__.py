from .interface import NotificationService
from .email_service import EmailNotificationService
from .dependencies import get_notification_service, get_template_manager, get_smtp_client

__all__ = [
    "NotificationService",
    "EmailNotificationService",
    "get_notification_service",
    "get_template_manager",
    "get_smtp_client",
]

