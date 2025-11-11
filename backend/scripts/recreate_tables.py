"""
Script pour recréer toutes les tables de la base de données.

Ce script:
1. Supprime toutes les tables existantes
2. Recrée toutes les tables selon les modèles SQLAlchemy

Usage:
    python -m scripts.recreate_tables
    ou
    uv run python scripts/recreate_tables.py
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


async def recreate_tables():
    """Supprime et recrée toutes les tables de la base de données."""
    
    database_url = settings.get_database_url()
    
    print(f"🔌 Connexion à la base de données...")
    print(f"   URL: {database_url.split('@')[1] if '@' in database_url else 'masquée'}")
    
    engine = create_async_engine(database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Étape 1: Supprimer toutes les tables
            print("\n🗑️  Étape 1: Suppression des tables existantes...")
            await conn.run_sync(Base.metadata.drop_all)
            
            # Vérifier et supprimer les tables restantes (pour PostgreSQL)
            if "postgresql" in database_url:
                result = await conn.execute(text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                """))
                tables = [row[0] for row in result.fetchall()]
                for table in tables:
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            print("   ✅ Toutes les tables ont été supprimées")
            
            # Étape 2: Créer toutes les tables
            print("\n🔨 Étape 2: Création des nouvelles tables...")
            await conn.run_sync(Base.metadata.create_all)
            
            # Lister les tables créées
            if "postgresql" in database_url:
                result = await conn.execute(text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"   📋 Tables créées ({len(tables)}):")
                for table in tables:
                    print(f"      - {table}")
            
            print("   ✅ Toutes les tables ont été créées")
        
        print("\n✅ Base de données recréée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la recréation des tables: {e}")
        raise
    finally:
        await engine.dispose()
        print("\n🔌 Connexion fermée")


async def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("🔄 RECRÉATION DES TABLES DE LA BASE DE DONNÉES")
    print("=" * 60)
    print("\n⚠️  ATTENTION: Cette opération va:")
    print("   1. Supprimer TOUTES les tables existantes")
    print("   2. Recréer les tables selon les modèles actuels")
    print("   Toutes les données seront perdues.\n")
    
    try:
        await recreate_tables()
    except KeyboardInterrupt:
        print("\n\n❌ Opération interrompue par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

