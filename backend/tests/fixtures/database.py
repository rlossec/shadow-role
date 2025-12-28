"""
Fixtures pour la configuration de la base de données de test.
"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, engine

# Configuration de la base de données de test
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
        # Configurer les factories avec la session
        from tests.factories.helpers import setup_factories, clear_factories
        setup_factories(session)
        yield session
        await session.rollback()
        clear_factories()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Setup test database and clean up after all tests."""
    yield
    await test_engine.dispose()
