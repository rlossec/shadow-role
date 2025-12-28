# Tests du backend Shadow Role

## 📁 Structure

```
tests/
├── conftest.py                      # Configuration pytest et fixtures
├── test_db_connection.py            # Script de test de connexion à la base de données
├── app/
│   ├── api/                         # Tests d'intégration API REST
│   │   └── authentication/
│   │       ├── README.md
│   │       ├── test_auth_register.py
│   │       └── test_auth_login.py
│   ├── services/                    # Tests unitaires des services
│   └── websocket/                   # Tests WebSocket
│       ├── unit/                    # Tests unitaires (avec mocks)
│       │   └── test_game_command_handler.py
│       └── e2e/                     # Tests end-to-end (avec serveur réel)
│           └── test_e2e_qui_suis_je.py
└── fixtures/                        # Fixtures partagées
```

## 🚀 Lancer les tests

```bash
uv sync          # Installer les dépendances de test
uv run pytest    # Lancer tous les tests
uv run pytest -v # Avec output détaillé
```

### Debugger les Tests

```bash
# Arrêter au premier échec
uv run pytest -x

# Afficher les print statements
uv run pytest -s

# Mode très verbeux
uv run pytest -vv
```

Autres détails :

```bash
uv run pytest --cov=. --cov-report=html # Avec couverture de code
uv run pytest --cov=backend --cov-report=html # Avec couverture et rapport HTML (ouvrir htmlcov/index.html)
```

## 📋 Types de tests

### Tests d'authentification

Tests pour les endpoints d'authentification (`/auth/register`, `/auth/jwt/login`).

**Fonctionnalités testées :**

- ✅ Enregistrement d'utilisateur avec validation
- ✅ Connexion avec username ou email
- ✅ Validation des champs (username, email, password, confirm_password)
- ✅ Gestion des erreurs (duplicatas, credentials invalides, etc.)

### Tests WebSocket

#### Tests unitaires (`tests/app/websocket/unit/`)

Tests des handlers WebSocket utilisant des mocks pour isoler la logique métier.

**Fonctionnalités testées :**

- ✅ Handlers de commande de jeu (GameCommandHandler)
- ✅ Gestion des phases de jeu
- ✅ Gestion des suggestions
- ✅ Attribution des missions
- ✅ Validation des missions

**Exécution :**

```bash
uv run pytest tests/app/websocket/unit/ -v
```

#### Tests E2E (`tests/app/websocket/e2e/`)

Tests end-to-end avec un vrai serveur WebSocket démarré pour chaque test.

**Fonctionnalités testées :**

- ✅ Flux complet de jeu depuis la création du lobby jusqu'à la fin
- ✅ Connexions WebSocket multiples avec authentification JWT
- ✅ Communication temps réel entre joueurs
- ✅ Scénarios complets de jeu

**Exécution :**

```bash
uv run pytest tests/app/websocket/e2e/ -v -s
```

**Note :** Les tests E2E sont plus lents car ils démarrent un vrai serveur. Utilisez les tests unitaires pour le développement itératif.

### Test de connexion à la base de données

Tests pytest pour vérifier la connexion à la base de données de production/dev et la création des tables.

**Fonctionnalités :**

- ✅ Test de connexion PostgreSQL/SQLite
- ✅ Création automatique des tables
- ✅ Liste des tables créées
- ✅ Utilise pytest et réutilise la configuration de `conftest.py` (pas de duplication)

## 🔧 Configuration

### Fixtures disponibles

Les fixtures sont définies dans `conftest.py` :

- `client` : Client HTTP async pour tester l'API (utilise la DB de test)
- `db_session` : Session de base de données pour les tests (SQLite en mémoire)
- `production_engine` : Engine SQLAlchemy pour la base de données de production/dev

### Base de données de test

Les tests utilisent **SQLite en mémoire** par défaut, ce qui signifie :

- Chaque test a une base de données propre
- Aucune persistance entre les tests
- Tests isolés et reproductibles

## 📝 Notes importantes

1. **Isolation** : Chaque test est isolé et utilise une session de base de données séparée.
2. **Fixtures** : Les fixtures `client` et `db_session` sont définies dans `tests/conftest.py`.
3. **Modèles** : Tous les modèles doivent être importés pour que `Base.metadata.create_all` fonctionne correctement.
4. **Authentification flexible** : L'authentification fonctionne avec username ou email.

## 🆕 Ajout de nouveaux tests

Pour ajouter un nouveau test :

1. Créez une fonction de test avec le préfixe `test_`
2. Utilisez le décorateur `@pytest.mark.asyncio` pour les tests async
3. Utilisez les fixtures `client` et/ou `db_session`
4. Faites des assertions claires et précises

**Exemple :**

```python
@pytest.mark.asyncio
async def test_my_new_test(client, db_session):
    # Setup
    ...

    # Action
    response = await client.post(...)

    # Assertion
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

## Tests spécifiques

### Tests API

```bash
# Tous les tests d'authentification
uv run pytest tests/app/api/authentication/ -v

# Tests de register uniquement
uv run pytest tests/app/api/authentication/test_auth_register.py -v

# Tests de login uniquement
uv run pytest tests/app/api/authentication/test_auth_login.py -v

# Un test spécifique
uv run pytest tests/app/api/authentication/test_auth_register.py::test_register_success -v
uv run pytest tests/app/api/authentication/test_auth_login.py::test_login_success_with_username -v
```

### Tests WebSocket

```bash
# Tous les tests unitaires WebSocket
uv run pytest tests/app/websocket/unit/ -v

# Tests E2E WebSocket
uv run pytest tests/app/websocket/e2e/ -v -s

# Un test spécifique
uv run pytest tests/app/websocket/unit/test_game_command_handler.py::test_start_game_success -v
uv run pytest tests/app/websocket/e2e/test_e2e_qui_suis_je.py -v -s
```

### Test de connexion à la base de données

```bash
# Test de connexion (pytest)
uv run pytest tests/test_db_connection.py -v

# Test spécifique
uv run pytest tests/test_db_connection.py::test_database_connection -v
uv run pytest tests/test_db_connection.py::test_table_creation -v
```

## 📚 Ressources

- [Documentation Pytest](https://docs.pytest.org/)
- [Documentation FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Documentation httpx](https://www.python-httpx.org/)
