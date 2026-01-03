# Backend — Documentation de référence

## Architecture générale

Le backend ShadowRole repose sur **FastAPI** avec

- une API REST
- un ajout **Socket.IO** pour la communication temps réel.

## Arborescence

```
backend/
├── api/                  # Routes REST (routers FastAPI)
├── core/                 # Configuration, constantes
├── db/
│   └── database.py       # Session SQLAlchemy / connexion
├── models/               # Modèles SQLAlchemy
├── repositories/         # Accès aux données et requêtes
├── schemas/              # Schémas Pydantic
├── scripts/              # Scripts utilitaires (migration, reset…)
├── services/             # Logique métier (assignation, jeu…)
├── tests/                # Tests unitaires et d’intégration
├── utils/                # Fonctions utilitaires transverses
├── websocket/            # Gestion Socket.IO (events, manager…)
└── main.py               # Point d'entrée FastAPI
```

## Documentation

### 📖 Documentation Principale

- **[Orchestration Handlers ↔ Services](./orchestration.md)** - **Référence complète** : Détails de l'orchestration entre handlers et services, responsabilités et méthodes principales de tous les composants

### 📚 Documentation par Thème

#### Architecture

- [Architecture Backend](./backend_architecture.md) - Vue d'ensemble de l'architecture et des couches

#### API et Communication

- [Référence API REST](./API_REFERENCE.md) - Endpoints REST FastAPI
- [WebSocket](./websocket.md) - Communication temps réel Socket.IO

#### Authentification

- [Authentification](./authentication.md) - Système d'authentification JWT complet

#### Tests

- [Tests backend](./tests.md) - Tests unitaires et d'intégration
