# Architecture du Backend

Ce document fournit une vue d'ensemble de l'architecture du backend ShadowRole.

> **📖 Documentation détaillée** : Pour les détails complets sur l'orchestration entre handlers et services, leurs responsabilités et méthodes principales, consultez [ORCHESTRATION.md](./ORCHESTRATION.md).

## Vue d'ensemble

Le backend s'articule entre trois couches principales :

- **Infrastructure WebSocket** : Gestion des connexions Socket.IO
- **Handlers** : Orchestration entre WebSocket et services métier
- **Services métier** : Logique métier pure (sans WebSocket)

```
┌─────────────────────────────────────────────────────────┐
│                    websocket/                           │
│  ┌──────────────┐               ┌──────────────┐        │
│  │ socket_server│               │   manager    │        │
│  └──────┬───────┘               └──────┬───────┘        │
└─────────┼──────────────────────────────┼────────────────┘
          │                              │
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────────────┐
│                    handlers/                            │
│  ┌──────────────┐               ┌───────────────┐       │
│  │LobbyCommand  │               │GameCommand    │       │
│  │Handler       │               │Handler        │       │
│  └──────┬───────┘               └──────┬────────┘       │
└─────────┼──────────────────────────────┼────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────────────┐
│                    services/                            │
│    ┌──────────────────────────────────────────┐         │
│    │  PhaseService  │  LobbyCommandService    │         │
│    │  Suggestion    │  LobbyQueryService      │         │
│    │  MissionAssi.. │  RoundService           │         │
│    │  MissionSel... │  ScoreService           │         │
│    └──────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

## Structure des Répertoires

```
backend/
├── api/                  # Routes REST (routers FastAPI)
├── core/                 # Configuration, constantes
├── db/
│   └── database.py       # Session SQLAlchemy / connexion
├── models/               # Modèles SQLAlchemy
├── repositories/         # Accès aux données et requêtes
├── schemas/              # Schémas Pydantic
├── handlers/             # Orchestration WebSocket + Services
│   ├── lobby_command_handler.py
│   └── game_command_handler.py
├── services/             # Logique métier
│   ├── phase_service.py
│   ├── lobby_command_service.py
│   ├── lobby_query_service.py
│   ├── suggestion_service.py
│   ├── round_service.py
│   ├── score_service.py
│   ├── mission_pool_service.py
│   ├── mission_selection_service.py
│   ├── mission_assignment_service.py
│   └── interfaces/       # Interfaces (Protocols)
├── websocket/            # Infrastructure WebSocket
│   ├── socket_server.py  # Point d'entrée Socket.IO
│   ├── manager.py        # Gestion des connexions
│   └── schemas/          # Schémas WebSocket
├── scripts/              # Scripts utilitaires
├── tests/                # Tests unitaires et d'intégration
├── utils/                # Fonctions utilitaires
└── main.py               # Point d'entrée FastAPI
```

## Couches Architecturales

### 1. Infrastructure WebSocket

**Localisation** : `websocket/`

**Responsabilités** :

- Gestion des connexions Socket.IO
- Authentification des utilisateurs (JWT)
- Gestion des rooms (join/leave)
- Communication WebSocket (send_to, broadcast)
- Mapping sid ↔ user_id ↔ lobby_id

**Composants principaux** :

- `socket_server.py` : Point d'entrée, configuration Socket.IO
- `manager.py` : WebSocketManager (infrastructure pure)

Voir [Documentation WebSocket](./websocket/README.md) pour plus de détails.

### 2. Handlers

**Localisation** : `handlers/`

**Responsabilités** :

- Orchestration des services métier
- Transformation événements WebSocket → appels services
- Broadcast des événements WebSocket aux clients

**Composants principaux** :

- `lobby_command_handler.py` : Opérations de lobby
- `game_command_handler.py` : Flux de jeu

> **📖 Détails complets** : Voir [ORCHESTRATION.md](./ORCHESTRATION.md) pour les responsabilités, dépendances et méthodes principales de chaque handler.

### 3. Services Métier

**Localisation** : `services/`

**Responsabilités** :

- Logique métier pure (indépendante de WebSocket)
- Validation des règles métier
- Accès aux données via repositories

**Services disponibles** :

- `PhaseService` : Gestion des phases et statuts
- `LobbyCommandService` / `LobbyQueryService` : Opérations lobby (CQRS)
- `SuggestionService` : Gestion des suggestions
- `MissionPoolService` : Pool de missions disponibles
- `MissionSelectionService` : Sélection des missions
- `MissionAssignmentService` : Attribution des missions
- `RoundService` : Gestion des rounds
- `ScoreService` : Calcul des scores

> **📖 Détails complets** : Voir [ORCHESTRATION.md](./ORCHESTRATION.md) pour les responsabilités, dépendances et méthodes principales de chaque service.

### 4. Repositories

**Localisation** : `repositories/`

**Responsabilités** :

- Accès aux données (abstraction de la base de données)
- Requêtes SQLAlchemy
- Pattern Repository pour isolation de la persistance

## Points d'Entrée

### API REST (`api/`)

Endpoints FastAPI pour les opérations CRUD et l'authentification.

Voir [Référence API REST](./API_REFERENCE.md) pour la liste complète des endpoints.

### WebSocket (`websocket/socket_server.py`)

Événements Socket.IO pour la communication temps réel.

**Événements Lobby** :

- `join_lobby`, `register_player`, `unregister_player`, `sync_lobby_state`

**Événements Jeu** :

- `start_game`, `end_game`, `send_suggestion`, `validate_suggestion`, `start_round`, `finalize_round`, `host_validate_mission`

> **📖 Détails complets** : Voir [ORCHESTRATION.md](./ORCHESTRATION.md) pour le mapping complet des événements WebSocket et leur orchestration.

## Documentation Complémentaire

- [orchestration.md](./orchestration.md) - **Référence principale** : Détails complets sur handlers et services
- [WebSocket](./websocket.md) - Détails sur l'infrastructure WebSocket
- [Authentification](./authentication.md) - Système d'authentification
