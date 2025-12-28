"""
Fixtures pour les services d'authentification et de notification.
"""

import pytest

from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.services.auth.service import build_authentication_service
from app.services.auth.token_manager import AccountActivationTokenManager
from app.services.auth.link_builder import NotificationLinkBuilder
from app.services.notifications.interface import NotificationService


class DummyNotificationService(NotificationService):
    """Service de notification factice pour les tests."""
    
    def __init__(self) -> None:
        self.calls = []

    async def send(self, to: str, template_name: str, context: dict[str, object]) -> None:
        self.calls.append({"to": to, "template": template_name, "context": context})


@pytest.fixture(scope="function")
def notification_service():
    """Fixture pour un service de notification factice."""
    return DummyNotificationService()


@pytest.fixture(scope="function")
def link_builder():
    """Fixture pour un builder de liens de notification."""
    return NotificationLinkBuilder(base_url="http://frontend.test")


@pytest.fixture(scope="function")
def auth_service(db_session, notification_service, link_builder):
    """Authentication service wired to the test session."""
    user_repo = UserRepository(db_session)
    token_repo = TokenRepository(db_session)
    return build_authentication_service(
        user_repo,
        token_repo,
        notification_service=notification_service,
        link_builder=link_builder,
    )


@pytest.fixture(scope="function")
def account_activation_manager(db_session):
    """Account activation token manager wired to the test session."""
    user_repo = UserRepository(db_session)
    return AccountActivationTokenManager(user_repo)
