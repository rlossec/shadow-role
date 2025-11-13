"""Configuration pytest for tests."""
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, engine, get_async_session
from main import app
from models import *  # Import all models so Base.metadata knows about them
from repositories.user_repository import UserRepository
from repositories.token_repository import TokenRepository
from repositories.gametype_repository import GameTypeRepository
from services.auth.service import build_authentication_service
from services.auth.token_manager import AccountActivationTokenManager
from services.auth.link_builder import NotificationLinkBuilder
from services.notifications.interface import NotificationService
from services.notifications.dependencies import get_notification_service as get_notification_service_dependency
from tests.api.helpers import init_game_types


default_db_url = "sqlite+aiosqlite:///:memory:"

# Créer un moteur de test avec SQLite en mémoire
test_engine = create_async_engine(
    default_db_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Session factory pour les tests
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def production_engine():
    """Fixture pour l'engine de production (réelle)."""
    return engine


@pytest.fixture(scope="function", autouse=False)
async def cleanup_production_connections(production_engine):
    """Fixture qui nettoie le pool de connexions après chaque test utilisant production_engine."""
    yield
    # Attendre un peu pour s'assurer que toutes les connexions sont fermées
    import asyncio

    await asyncio.sleep(0.1)

    try:
        if hasattr(production_engine, "sync_engine") and hasattr(production_engine.sync_engine, "pool"):
            production_engine.sync_engine.pool.dispose()
    except AttributeError:
        pass


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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


class DummyNotificationService(NotificationService):
    def __init__(self) -> None:
        self.calls = []

    async def send(self, to: str, template_name: str, context: dict[str, object]) -> None:
        self.calls.append({"to": to, "template": template_name, "context": context})


@pytest.fixture(scope="function")
def notification_service():
    return DummyNotificationService()


@pytest.fixture(scope="function")
def link_builder():
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


@pytest.fixture(scope="function")
async def game_type_repository(db_session):
    """Game type repository wired to the test session."""
    return GameTypeRepository(db_session)


@pytest.fixture(scope="function")
async def initialized_game_types(db_session, game_type_repository):
    """
    Initialise les types de jeu de base pour les tests.
    
    Cette fixture peut être utilisée dans les tests qui ont besoin de types de jeu.
    Elle vérifie automatiquement si les types existent déjà pour éviter les doublons.
    
    Retourne un tuple (game_type_repository, list[GameType]) pour faciliter l'accès aux types.
    
    Exemple d'utilisation:
        async def test_create_game(client, initialized_game_types):
            game_type_repo, game_types = initialized_game_types
            mission_type = game_types[0]  # Premier type (Mission)
            # Utiliser mission_type.id pour créer un jeu
    """
    game_types = await init_game_types(game_type_repository)
    return game_type_repository, game_types


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Setup test database and clean up after all tests."""
    yield
    await test_engine.dispose()
