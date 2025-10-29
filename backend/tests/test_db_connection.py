"""
Script de test de connexion à la base de données.

Usage:
    python test_db_connection.py
"""

import asyncio
from sqlalchemy import text
from core.database import engine


async def test_connection():
    """Test the database connection."""
    try:
        async with engine.begin() as conn:
            # Essayer de récupérer la version (PostgreSQL)
            result = await conn.execute(text("SELECT version();"))
            version = (await result.fetchone())[0]
            print(f"✅ Connexion réussie à la base de données!")
            print(f"📊 Version PostgreSQL: {version}")
            return True
    except Exception as e1:
        try:
            # Si PostgreSQL échoue, essayer SQLite
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT sqlite_version();"))
                version = (await result.fetchone())[0]
                print(f"✅ Connexion réussie à la base de données!")
                print(f"📊 Version SQLite: {version}")
                return True
        except Exception as e2:
            print(f"❌ Erreur de connexion PostgreSQL: {e1}")
            print(f"❌ Erreur de connexion SQLite: {e2}")
            return False
    finally:
        await engine.dispose()


async def test_create_table():
    """Test the creation of tables."""
    try:
        from core.database import Base
        from models.user import User
        
        async with engine.begin() as conn:
            # Créer les tables
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully!")
            
            # Lister les tables (adapter selon le SGBD)
            db_type = str(engine.url.drivername)
            
            if "sqlite" in db_type:
                # SQLite
                result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            elif "postgresql" in db_type or "postgres" in db_type:
                # PostgreSQL
                result = await conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
            else:
                # Autre SGBD
                result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Tables disponibles: {', '.join(tables)}")
            return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔌 Test de connexion à la base de données...\n")
    
    # Test de connexion
    success = asyncio.run(test_connection())
    
    if success:
        print("\nTesting table creation...\n")
        asyncio.run(test_create_table())

