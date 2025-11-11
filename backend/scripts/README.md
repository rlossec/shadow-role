# Scripts de gestion de la base de données

Ce dossier contient des scripts utilitaires pour gérer la base de données.

## Scripts disponibles

### 1. `drop_tables.py` - Supprimer toutes les tables

Supprime toutes les tables de la base de données.

⚠️ **ATTENTION**: Cette opération est irréversible. Toutes les données seront perdues.

**Usage:**

```bash
# Depuis le dossier backend
python -m scripts.drop_tables

# Ou avec uv
uv run python scripts/drop_tables.py

# Ou directement
cd backend
python scripts/drop_tables.py
```

### 2. `recreate_tables.py` - Recréer les tables

Supprime toutes les tables existantes et les recrée selon les modèles SQLAlchemy actuels.

⚠️ **ATTENTION**: Cette opération est irréversible. Toutes les données seront perdues.

**Usage:**

```bash
# Depuis le dossier backend
python -m scripts.recreate_tables

# Ou avec uv
uv run python scripts/recreate_tables.py

# Ou directement
cd backend
python scripts/recreate_tables.py
```

## Quand utiliser ces scripts ?

### Utiliser `drop_tables.py` si:

- Vous voulez seulement supprimer les tables sans les recréer
- Vous allez créer les tables manuellement ou via des migrations

### Utiliser `recreate_tables.py` si:

- Vous avez modifié les modèles SQLAlchemy (comme changer les types d'ID de Integer à UUID)
- Vous voulez réinitialiser complètement la base de données
- Vous êtes en développement et voulez repartir de zéro

## Exemple d'utilisation après modification des modèles

Après avoir modifié les modèles (par exemple, conversion des IDs de Integer à UUID):

```bash
# 1. Supprimer et recréer les tables
uv run python scripts/recreate_tables.py

# 2. Redémarrer l'application
uv run uvicorn main:app --reload
```

## Notes

- Les scripts utilisent les paramètres de connexion définis dans `.env` (via `core.config.settings`)
- Assurez-vous que votre fichier `.env` est correctement configuré avant d'exécuter les scripts
