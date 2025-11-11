# Notes techniques — Backend

## Architecture générale

Le backend ShadowRole repose sur **FastAPI** pour l’API REST et sur **Socket.IO** pour la communication temps réel.  
L’organisation du code suit une approche inspirée de la _Clean Architecture_ : séparation claire entre couches API, services métier, accès aux données et WebSocket.

## Arborescence

```
backend/
├── main.py               # Point d'entrée FastAPI
├── api/                  # Routes REST (routers FastAPI)
├── core/                 # Configuration, constantes
├── db/
│   ├── schemas/          # Schémas Pydantic
│   └── database.py       # Session SQLAlchemy / connexion
├── models/               # Modèles SQLAlchemy
├── repositories/         # Accès aux données et requêtes
├── scripts/              # Scripts utilitaires (migration, reset…)
├── services/             # Logique métier (assignation, jeu…)
├── tests/                # Tests unitaires et d’intégration
├── utils/                # Fonctions utilitaires transverses
└── websocket/            # Gestion Socket.IO (events, manager…)
```

## Principes clés

- **API REST** : exposée via `backend/api`. Chaque module correspond à un domaine (authentification, lobby, game, player…).
- **Services** : la logique métier (ex. `GameService`, `AssignmentService`) encapsule les règles de jeu et orchestre les repositories.
- **Repositories** : centralisent les accès à la base (CRUD, requêtes spécifiques). Ils utilisent les modèles SQLAlchemy situés dans `backend/models`.
- **WebSocket** : géré dans `backend/websocket` avec un `ConnectionManager`, les schémas d’événements et les handlers Socket.IO.

## Ressources associées

- Documentation REST : `backend/api_reference.md`
- Schémas de données : `backend/db_schemas.md`
- Documentation temps réel : `backend/websocket_doc.md`
- Stratégie de tests : `backend/tests.md`
