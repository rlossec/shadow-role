# Architecture Générale - Shadow Role

Ce document présente une vue d'ensemble de l'architecture du système Shadow Role, les patterns utilisés et les principes de conception.

## Architecture en Couches

### Backend

```
┌─────────────────────────────────────────┐
│                API Layer                │
│  - Routers REST                         │
│  - Validation (Pydantic)                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│            WebSocket Layer              │
│  - WebSocketManager                     │
│  - Handlers (Lobby, Game)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│              Services Layer             │
│  - PhaseService                         │
│  - LobbyCommandService                  │
│  - LobbyQueryService                    │
│  - SuggestionService                    │
│  - MissionAssignmentService             │
│  - RoundService, ScoreService           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Repository Layer               │
│  - UserRepository                       │
│  - LobbyRepository                      │
│  - PlayerRepository                     │
│  - MissionRepository                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Models Layer (SQLAlchemy)          │
│  - User, Lobby, Player, Mission, etc.   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         PostgreSQL Database             │
└─────────────────────────────────────────┘
```

Pour plus de détail voir [Architecture du Backend](./backend/backend_architecture.md)

### Frontend

```
┌─────────────────────────────────────────┐
│      Presentation Layer (React)         │
│  - Pages                                │
│  - Components                           │
│  - Layouts                              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Hooks Layer                     │
│  - useAuth, useLobbies, useGames        │
│  - useWebSocket                         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│             Services Layer              │
│  - authService                          │
│  - lobbiesService                       │
│  - gamesService                         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      State Management                   │
│  - TanStack Query (Server State)        │
│  - Context API (Global State)           │
└─────────────────────────────────────────┘
```

## Patterns et Principes

- [Repository Pattern](./contributing/repository_pattern.md) pour plus de détails.
- [CQRS](./contributing/cqrs.md) pour plus de détails.
- L'injection de dépendances est gérée par FastAPI via `Depends()` :
- Single Responsibility Principle (SRP)

## Communication et Flux de Données

### REST API

Utilisée pour :

- Authentification
- CRUD des ressources (lobbies, games, missions)
- Opérations synchrones

Voir [Documentation API](./backend/README.md) pour plus de détails.

### WebSocket (Socket.IO)

Utilisée pour :

- Communication temps réel pendant les parties
- Synchronisation de l'état des lobbies
- Notifications en temps réel

Voir [Communication](./overview/communication.md) pour plus de détails.

## Sécurité

- **Authentification JWT** : Access tokens (courte durée) + Refresh tokens
- **Protection des routes** : Middleware d'authentification
- **Validation** : Pydantic pour la validation des données

Voir [Sécurité](./overview/security.md) pour plus de détails.
