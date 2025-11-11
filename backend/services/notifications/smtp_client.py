from __future__ import annotations

import contextlib
import logging
from email.message import EmailMessage
from typing import Optional

import aiosmtplib

from core.config import settings


logger = logging.getLogger(__name__)


class SMTPClient:
    """Client SMTP asynchrone minimaliste."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        from_email: str | None = None,
        use_tls: bool | None = None,
        use_starttls: bool | None = None,
        timeout: float | None = None,
    ) -> None:
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.username = username or settings.SMTP_USERNAME
        self.password = password or settings.SMTP_PASSWORD
        self.from_email = from_email or settings.SMTP_FROM_EMAIL or self.username or "no-reply@localhost"
        self.use_tls = use_tls if use_tls is not None else settings.SMTP_USE_TLS
        self.use_starttls = use_starttls if use_starttls is not None else settings.SMTP_USE_STARTTLS
        self.timeout = timeout if timeout is not None else settings.SMTP_TIMEOUT

    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
    ) -> None:
        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(text_content)

        if html_content:
            message.add_alternative(html_content, subtype="html")

        client = aiosmtplib.SMTP(
            hostname=self.host,
            port=self.port,
            use_tls=self.use_tls,
            start_tls=self.use_starttls,
            timeout=self.timeout,
        )

        try:
            await client.connect()
            if self.username and self.password:
                await client.login(self.username, self.password)
            await client.send_message(message)
            logger.info("Email sent to %s with subject '%s'", to_email, subject)
        except Exception as exc:  # pragma: no cover - log and propagate
            logger.exception("Failed to send email to %s: %s", to_email, exc)
            raise
        finally:
            if client.is_connected:
                with contextlib.suppress(Exception):
                    await client.quit()

