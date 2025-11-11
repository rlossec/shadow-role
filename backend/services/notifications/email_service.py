from __future__ import annotations

from typing import Any

from .interface import NotificationService
from .smtp_client import SMTPClient
from .template_manager import NotificationTemplateManager, TemplateNotFoundError


class EmailNotificationService(NotificationService):
    """Implémentation générique de NotificationService pour l’email."""

    def __init__(
        self,
        smtp_client: SMTPClient | None = None,
        template_manager: NotificationTemplateManager | None = None,
    ) -> None:
        self.smtp_client = smtp_client or SMTPClient()
        self.template_manager = template_manager or NotificationTemplateManager()

    async def send(self, to: str, template_name: str, context: dict[str, Any]) -> None:
        subject_path = f"{template_name}/subject.txt"
        text_path = f"{template_name}/body.txt"
        html_path = f"{template_name}/body.html"

        try:
            subject = self.template_manager.render(subject_path, context).strip()
            body_text = self.template_manager.render(text_path, context)
        except TemplateNotFoundError as exc:
            raise TemplateNotFoundError(f"Template manquant pour '{template_name}': {exc}") from exc

        try:
            body_html = self.template_manager.render(html_path, context)
        except TemplateNotFoundError:
            body_html = None

        await self.smtp_client.send_email(
            to_email=to,
            subject=subject,
            text_content=body_text,
            html_content=body_html,
        )

