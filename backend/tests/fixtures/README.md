# Fixtures de Tests

Ce répertoire contient les fixtures réutilisables pour tous les tests du projet.

## Structure

```
backend/tests/
├── fixtures/                    # Fixtures partagées
│   ├── scenarios/               # Scénarios de test organisés par catégorie
│   │   ├── users.py             # Fixtures pour les utilisateurs
│   │   ├── game.py              # Fixtures pour les jeux et missions
│   │   ├── lobby.py             # Fixtures pour les lobbies et joueurs
│   │   ├── game_session.py      # Scénarios complets de session de jeu
│   │   ├── __init__.py          # Exports publics
│   │   └── README.md            # Documentation détaillée des scénarios
│   ├── database.py              # Fixtures de base de données
│   ├── authentication.py        # Fixtures des services auth, notifications
│   ├── api.py                   # Fixtures pour les tests d'API
│   ├── __init__.py              # Exports publics
│   └── README.md                # Ce fichier
├── factories/                   # Factories pour créer des objets individuels
├── services/                    # Tests de services
├── api/                         # Tests d'API
└── conftest.py                  # Configuration pytest principale (imports des modèles)
```

## Organisation des Fixtures

Les fixtures sont organisées par catégorie :

### Scénarios (`scenarios/`)

Les scénarios de test sont organisés dans le dossier `scenarios/` avec des fichiers séparés selon les situations :

- **`users.py`** : Fixtures pour créer des utilisateurs (standards, administrateurs)
- **`game.py`** : Fixtures pour créer des jeux avec leurs missions
- **`lobby.py`** : Fixtures pour créer des lobbies avec ou sans joueurs
- **`game_session.py`** : Scénarios complets pour tester les handlers et services

📖 **Pour plus de détails sur les scénarios disponibles, consultez [scenarios/README.md](scenarios/README.md)**

### Base de données (`database.py`)

Configuration et fixtures de base de données :

- **`db_session`** : Session de base de données de test (créée/nettoyée pour chaque test)
- **`production_engine`** : Engine SQLAlchemy pour la base de production (utilisé dans `test_db_connection.py`)
- **`cleanup_production_connections`** : Nettoie les connexions de production après les tests
- **`setup_test_db`** : Setup global de la base de données de test (session scope)

### Authentification (`authentication.py`)

Services d'authentification et de notification pour les tests :

- **`notification_service`** : Service de notification factice (`DummyNotificationService`)
- **`link_builder`** : Builder de liens pour les notifications
- **`auth_service`** : Service d'authentification configuré pour les tests
- **`account_activation_manager`** : Gestionnaire de tokens d'activation de compte

### API (`api.py`)

Fixtures pour les tests d'API :

- **`client`** : Client HTTP async pour tester les endpoints API (FastAPI/httpx)

## Découverte Automatique

Les fixtures sont automatiquement disponibles dans tous les tests grâce à `conftest.py`.
Vous n'avez pas besoin de les importer explicitement :

```python
# ✅ Fonctionne automatiquement
async def test_my_feature(setup_lobby_with_players):
    # ...
```

## Réutilisation

Ces fixtures peuvent être utilisées dans :

- ✅ Tests de services (`tests/services/`)
- ✅ Tests d'API (`tests/api/`)
- ✅ Tests d'intégration (futurs)
- ✅ Tests WebSocket (futurs)

Elles sont partagées pour éviter la duplication de code et garantir la cohérence des données de test.

## Ajouter une Nouvelle Fixture

### Pour les scénarios

Consultez [scenarios/README.md](scenarios/README.md) pour savoir comment ajouter un nouveau scénario.

### Pour les autres catégories

1. Ajoutez la fixture dans le fichier approprié (`database.py`, `authentication.py`, ou `api.py`)
2. Si nécessaire, ajoutez-la dans `__init__.py` pour l'export
3. Les fixtures sont automatiquement découvertes par pytest via `conftest.py`
