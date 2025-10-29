## Backend — Documentation de référence

Ce README centralise les liens vers la documentation du backend. Utilisez-le comme point d'entrée pour naviguer vers les sections détaillées.

### 🚀 Démarrage rapide

```bash
# Installer les dépendances
uv sync

# Lancer le serveur
uv run uvicorn main:app --reload

# Lancer les tests
uv run pytest tests/ -v
```

### 🧪 Tests

Les tests sont organisés dans le dossier `tests/` :

- `tests/test_auth_register.py` : Tests d'enregistrement
- `tests/test_auth_login.py` : Tests de connexion
- `tests/test_auth_me.py` : Tests d'authentification

**Commandes utiles :**

```bash
# Lancer tous les tests
uv run pytest

# Lancer un fichier de test spécifique
uv run pytest tests/test_auth_register.py

# Lancer avec couverture de code
uv run pytest --cov=. --cov-report=html

# Lancer en mode verbose
uv run pytest -v
```

### Table des matières

- [Architecture](../docs/backend/architecture.md)
- [Base de données](../docs/backend/database.md)
- [Authentification](../docs/backend/authentication.md)
- [Endpoints API](../docs/backend/endpoints.md)
- [WebSocket](../docs/backend/websocket.md)

### Notes

- Les documents se trouvent dans `docs/backend` et sont versionnés avec le code.
- Mettez à jour ces liens si la structure des dossiers évolue.
