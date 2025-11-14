# Backend — Documentation de référence

Ce README centralise les liens vers la documentation du backend. Utilisez-le comme point d’entrée pour naviguer vers les sections détaillées.

## Documentation

On retrouve les éléments clés détaillé dans ces fichiers :

- [Référence API REST](./api_reference.md)
- [Documentation WebSocket](./websocket_doc.md)
- [Tests backend](./tests.md)

## Architecture générale

Le backend ShadowRole repose sur **FastAPI** avec

- une API REST
- un ajout **Socket.IO** pour la communication temps réel.

L’organisation du code suit une approche inspirée de la _Clean Architecture_ : séparation claire entre couches API, services métier, accès aux données et WebSocket.

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
