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
from services.auth.service import build_authentication_service


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
async def client(db_session):
    """Async HTTP client bound to the test DB."""

    async def override_get_async_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_service(db_session):
    """Authentication service wired to the test session."""
    user_repo = UserRepository(db_session)
    return build_authentication_service(user_repo)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Setup test database and clean up after all tests."""
    yield
    await test_engine.dispose()
