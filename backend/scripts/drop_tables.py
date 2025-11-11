"""
Script pour supprimer toutes les tables de la base de données.

⚠️ ATTENTION : Ce script supprime TOUTES les tables de la base de données.
Toutes les données seront perdues de manière irréversible.

Usage:
    python -m scripts.drop_tables
    ou
    uv run python scripts/drop_tables.py
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from db.database import Base
from models import *  # Importer tous les modèles pour que Base.metadata les connaisse


async def drop_all_tables():
    """Supprime toutes les tables de la base de données."""
    
    database_url = settings.get_database_url()
    
    print(f"🔌 Connexion à la base de données...")
    print(f"   URL: {database_url.split('@')[1] if '@' in database_url else 'masquée'}")
    
    engine = create_async_engine(database_url, echo=False)
    
    try:
        metadata_error = None

        # Méthode 1: Utiliser SQLAlchemy metadata pour supprimer les tables
        print("\n🗑️  Suppression des tables via SQLAlchemy metadata...")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            print("   ✅ Tables supprimées via metadata")
        except Exception as err:
            metadata_error = err
            print(f"   ⚠️  Impossible de supprimer via metadata: {err}")
            print("   ➜ Tentative de suppression manuelle avec CASCADE.")
        
        # Méthode 2: Vérifier s'il reste des tables et les supprimer manuellement
        # (utile pour les tables créées manuellement ou les vues)
        print("\n🔍 Vérification des tables restantes...")
        remaining_tables = []
        failed_tables = []
        
        # Pour PostgreSQL
        if "postgresql" in database_url:
            async def fetch_postgres_tables():
                async with engine.connect() as conn:
                    result = await conn.execute(text("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                    """))
                    return [row[0] for row in result.fetchall()]

            tables = await fetch_postgres_tables()
            
            if tables:
                print(f"   📋 Tables trouvées: {', '.join(tables)}")
                # Supprimer les tables restantes
                for table in tables:
                    try:
                        async with engine.begin() as conn:
                            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                        print(f"   ✅ Table '{table}' supprimée")
                    except Exception as e:
                        failed_tables.append(table)
                        print(f"   ⚠️  Erreur lors de la suppression de '{table}': {e}")

                remaining_tables = await fetch_postgres_tables()
            else:
                print("   ✅ Aucune table restante")
        
        # Pour SQLite
        elif "sqlite" in database_url:
            async def fetch_sqlite_tables():
                async with engine.connect() as conn:
                    result = await conn.execute(text("""
                        SELECT name 
                        FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """))
                    return [row[0] for row in result.fetchall()]

            tables = await fetch_sqlite_tables()
            
            if tables:
                print(f"   📋 Tables trouvées: {', '.join(tables)}")
                for table in tables:
                    try:
                        async with engine.begin() as conn:
                            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}"'))
                        print(f"   ✅ Table '{table}' supprimée")
                    except Exception as e:
                        failed_tables.append(table)
                        print(f"   ⚠️  Erreur lors de la suppression de '{table}': {e}")

                remaining_tables = await fetch_sqlite_tables()
            else:
                print("   ✅ Aucune table restante")
        else:
            print("   ⚠️  Type de base de données non géré pour la suppression manuelle.")
        
        if failed_tables:
            raise RuntimeError(f"Impossible de supprimer certaines tables: {', '.join(failed_tables)}")

        if remaining_tables:
            raise RuntimeError(f"Des tables subsistent dans la base: {', '.join(remaining_tables)}")

        if metadata_error and not remaining_tables:
            print("   ✅ Suppression manuelle réussie malgré l'échec initial.")
        
        print("\n✅ Toutes les tables ont été supprimées avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la suppression des tables: {e}")
        raise
    finally:
        await engine.dispose()
        print("\n🔌 Connexion fermée")


async def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("🗑️  SUPPRESSION DE TOUTES LES TABLES DE LA BASE DE DONNÉES")
    print("=" * 60)
    print("\n⚠️  ATTENTION: Cette opération est irréversible!")
    print("   Toutes les données seront perdues.\n")
    
    # Demander confirmation (optionnel, commenté pour l'automatisation)
    # response = input("Êtes-vous sûr de vouloir continuer? (oui/non): ")
    # if response.lower() != "oui":
    #     print("❌ Opération annulée.")
    #     return
    
    try:
        await drop_all_tables()
    except KeyboardInterrupt:
        print("\n\n❌ Opération interrompue par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

