"""
Fixtures pour les tests d'API.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.db.database import get_async_session
from main import app
from app.services.notifications.dependencies import get_notification_service as get_notification_service_dependency


@pytest.fixture(scope="function")
async def client(db_session, notification_service):
    """Async HTTP client bound to the test DB."""
    async def override_get_async_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[get_notification_service_dependency] = lambda: notification_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()
