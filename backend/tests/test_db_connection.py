"""
Tests de connexion à la base de données de production.

Ces tests vérifient la connexion à la base de données réelle (production/dev).
Ils utilisent pytest et réutilisent la configuration de conftest.py.

Usage:
    # Lancer avec pytest (recommandé)
    uv run pytest tests/test_db_connection.py -v
    
    # Lancer un test spécifique
    uv run pytest tests/test_db_connection.py::test_database_connection -v
    uv run pytest tests/test_db_connection.py::test_table_creation -v
"""

from typing import Tuple, Optional

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Result

from app.db.database import Base


@pytest.mark.asyncio
async def test_database_connection(production_engine, cleanup_production_connections):
    """
    Test the database connection to the production database.
    
    This test verifies that we can connect to the real database
    (as opposed to the test database used in other tests).
    """
    db_type: str = str(production_engine.url.drivername).lower()
    
    # Utiliser connect() pour les opérations de lecture seule (pas de transaction)
    async with production_engine.connect() as conn:
        if "postgresql" in db_type or "postgres" in db_type:
            # PostgreSQL
            result: Result = await conn.execute(text("SELECT version();"))
            row: Optional[Tuple[str, ...]] = result.fetchone()
            assert row is not None, "Failed to get PostgreSQL version"
            version: str = row[0]
            print(f"\n✅ Connexion réussie à la base de données!")
            print(f"📊 Version PostgreSQL: {version}")
        elif "sqlite" in db_type:
            # SQLite
            result: Result = await conn.execute(text("SELECT sqlite_version();"))
            row: Optional[Tuple[str, ...]] = result.fetchone()
            assert row is not None, "Failed to get SQLite version"
            version: str = row[0]
            print(f"\n✅ Connexion réussie à la base de données!")
            print(f"📊 Version SQLite: {version}")
        else:
            # Type inconnu, essayer PostgreSQL puis SQLite
            try:
                result: Result = await conn.execute(text("SELECT version();"))
                row: Optional[Tuple[str, ...]] = result.fetchone()
                if row:
                    version: str = row[0]
                    print(f"\n✅ Connexion réussie à la base de données!")
                    print(f"📊 Version: {version}")
            except Exception:
                # Essayer SQLite
                result: Result = await conn.execute(text("SELECT sqlite_version();"))
                row: Optional[Tuple[str, ...]] = result.fetchone()
                assert row is not None, "Failed to get database version"
                version: str = row[0]
                print(f"\n✅ Connexion réussie à la base de données!")
                print(f"📊 Version SQLite: {version}")


@pytest.mark.asyncio
async def test_table_creation(production_engine, cleanup_production_connections):
    """
    Test the creation of tables in the production database.
    
    This test creates all tables and lists them to verify
    that the database schema is correctly set up.
    """
    db_type: str = str(production_engine.url.drivername).lower()
    
    # Utiliser begin() pour créer les tables (nécessite une transaction)
    async with production_engine.begin() as conn:
        # Créer les tables (tous les modèles doivent être importés dans conftest.py)
        await conn.run_sync(Base.metadata.create_all)
        print("\n✅ Tables créées avec succès!")
    
    # Utiliser une connexion séparée pour lister les tables (lecture seule)
    async with production_engine.connect() as list_conn:
        # Lister les tables (adapter selon le SGBD)
        if "sqlite" in db_type:
            # SQLite
            result: Result = await list_conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
        elif "postgresql" in db_type or "postgres" in db_type:
            # PostgreSQL
            result: Result = await list_conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
        else:
            # Autre SGBD (par défaut SQLite)
            result: Result = await list_conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
        
        rows = result.fetchall()
        tables: list[str] = [row[0] for row in rows]
        print(f"📋 Tables disponibles ({len(tables)}): {', '.join(tables)}")
        
        # Vérifier qu'au moins quelques tables sont présentes
        assert len(tables) > 0, "No tables found in database"
        assert "users" in tables, "Users table not found"

