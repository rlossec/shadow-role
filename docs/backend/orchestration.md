# Orchestration Handlers ↔ Services

Ce document détaille l'orchestration entre les handlers et les services du backend, leurs responsabilités respectives et leurs principales méthodes.

## Vue d'ensemble

L'architecture suit une séparation claire des responsabilités :

```
┌─────────────────────────────────────────────────────────────┐
│                    WebSocket Events                         │
│              (socket_server.py)                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Handlers                               │
│  Responsabilités :                                          │
│  - Orchestration des services                               │
│  - Transformation événements WebSocket → appels services    │
│  - Broadcast des événements WebSocket                       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Services Métier                          │
│  Responsabilités :                                          │
│  - Logique métier pure                                      │
│  - Validation des règles métier                             │
│  - Accès aux données via repositories                       │
└─────────────────────────────────────────────────────────────┘
```

## Handlers

Les handlers sont la couche d'orchestration entre WebSocket et les services métier.

### LobbyCommandHandler

**Fichier** : `backend/app/handlers/lobby_command_handler.py`

**Responsabilités** :

- ✅ Orchestration des opérations de lobby (connexions + joueurs)
- ✅ Transformation événements WebSocket → appels services
- ✅ Broadcast des événements WebSocket aux clients

**Méthodes principales** :

| Méthode                                        | Description                                |
| ---------------------------------------------- | ------------------------------------------ |
| `join_lobby(sid, lobby_id)`                    | Utilisateur rejoint un lobby via WebSocket |
| `leave_lobby(sid, lobby_id)`                   | Utilisateur quitte un lobby                |
| `register_player(sid, lobby_id, alias, color)` | Inscrire un utilisateur comme joueur       |
| `unregister_player(lobby_id, user_id)`         | Désinscrire un joueur d'un lobby           |

### GameCommandHandler

**Fichier** : `backend/app/handlers/game_command_handler.py`

**Responsabilités** :

- ✅ Orchestration du flux de jeu (phases, rounds, suggestions, missions)
- ✅ Transformation événements WebSocket → appels services spécialisés
- ✅ Broadcast des événements de jeu
- ✅ Distribution privée des missions aux joueurs

**Méthodes principales** :

#### Gestion du jeu

| Méthode                             | Description               |
| ----------------------------------- | ------------------------- |
| `start_game(lobby_id)`              | Démarrer une partie       |
| `end_game(lobby_id)`                | Terminer une partie       |
| `start_game_phase(lobby_id, phase)` | Démarrer une phase de jeu |

#### Gestion des suggestions

| Méthode                                                          | Description                          |
| ---------------------------------------------------------------- | ------------------------------------ |
| `send_suggestion(lobby_id, user_id, ...)`                        | Un joueur propose une suggestion     |
| `validate_suggestion(lobby_id, host_user_id, temp_id, accepted)` | L'hôte valide/rejette une suggestion |

#### Gestion des rounds

| Méthode                                 | Description                                 |
| --------------------------------------- | ------------------------------------------- |
| `start_round(lobby_id, mission_source)` | Démarrer un round et attribuer les missions |
| `finalize_round(lobby_id)`              | Finaliser un round                          |

#### Validation des missions

| Méthode                                                                                 | Description                              |
| --------------------------------------------------------------------------------------- | ---------------------------------------- |
| `host_validate_mission(lobby_id, host_user_id, player_id, assigned_mission_id, result)` | L'hôte valide une mission (success/fail) |

## Structure des Services

```
backend/app/services/
├── auth/                    # Authentification
│   ├── service.py           # AuthenticationService
│   ├── token_manager.py     # Token managers
│   └── dependencies.py      # Factories
├── lobby_command_service.py # Commandes lobby (CQRS)
├── lobby_query_service.py   # Requêtes lobby (CQRS)
├── phase_service.py         # Gestion des phases
├── suggestion_service.py    # Gestion des suggestions
├── mission_pool_service.py  # Pool de missions
├── mission_selection_service.py # Sélection de missions
├── mission_assignment_service.py # Attribution de missions
├── round_service.py         # Gestion des rounds
├── score_service.py         # Calcul des scores
└── interfaces/              # Interfaces/Protocols
```

### Services de Jeu

| Service        | Fichier            | Responsabilité principale          |
| -------------- | ------------------ | ---------------------------------- |
| `PhaseService` | `phase_service.py` | Gestion des phases et statuts      |
| `RoundService` | `round_service.py` | Gestion du cycle de vie des rounds |
| `ScoreService` | `score_service.py` | Calcul et persistance des scores   |

### Services de Lobby

| Service               | Fichier                    | Responsabilité principale                   |
| --------------------- | -------------------------- | ------------------------------------------- |
| `LobbyCommandService` | `lobby_command_service.py` | Opérations de modification (CQRS - Command) |
| `LobbyQueryService`   | `lobby_query_service.py`   | Opérations de lecture (CQRS - Query)        |

### Services de Missions

| Service                    | Fichier                         | Responsabilité principale            |
| -------------------------- | ------------------------------- | ------------------------------------ |
| `SuggestionService`        | `suggestion_service.py`         | Gestion des suggestions temporaires  |
| `MissionPoolService`       | `mission_pool_service.py`       | Pool de missions disponibles         |
| `MissionSelectionService`  | `mission_selection_service.py`  | Sélection des missions (wrapper)     |
| `MissionAssignmentService` | `mission_assignment_service.py` | Attribution des missions aux joueurs |

### Services d'Authentification

| Service                 | Fichier           | Responsabilité principale                 |
| ----------------------- | ----------------- | ----------------------------------------- |
| `AuthenticationService` | `auth/service.py` | Inscription, authentification, tokens JWT |

Voir [Authentification](./authentication.md) pour plus de détails sur `AuthenticationService`.

### PhaseService

**Fichier** : `backend/app/services/phase_service.py`

**Responsabilités** :

- ✅ Gestion des phases de jeu (NONE, SUGGESTION, ROUND, VALIDATION)
- ✅ Gestion des statuts (WAITING, RUNNING, PAUSED, ENDED)
- ✅ Validation des transitions de phases
- ✅ Gestion des rounds (création, numérotation)

**Dépendances** :

- `LobbyRepository`
- `PlayerRepository`
- `RoundRepository`
- `MissionSelectionService` (pour validation du pool)

**Méthodes principales** :

| Méthode                            | Description                                | Retour               |
| ---------------------------------- | ------------------------------------------ | -------------------- |
| `start_game(lobby_id)`             | Démarrer une partie (WAITING → RUNNING)    | `Lobby`              |
| `end_game(lobby_id)`               | Terminer une partie (→ ENDED)              | `Lobby`              |
| `pause_game(lobby_id)`             | Mettre en pause (RUNNING → PAUSED)         | `Lobby`              |
| `resume_game(lobby_id)`            | Reprendre (PAUSED → RUNNING)               | `Lobby`              |
| `get_current_phase(lobby_id)`      | Obtenir la phase actuelle                  | `str` (phase)        |
| `get_current_status(lobby_id)`     | Obtenir le statut actuel                   | `str` (status)       |
| `set_phase(lobby_id, phase)`       | Changer de phase (avec validation)         | `Lobby`              |
| `start_suggestion_phase(lobby_id)` | Démarrer phase suggestion                  | `Lobby`              |
| `end_suggestion_phase(lobby_id)`   | Terminer phase suggestion                  | `Lobby`              |
| `start_round(lobby_id)`            | Démarrer un round (création + phase ROUND) | `int` (round_number) |
| `end_round_phase(lobby_id)`        | Terminer phase round                       | `Lobby`              |
| `start_validation_phase(lobby_id)` | Démarrer phase validation                  | `Lobby`              |
| `end_validation_phase(lobby_id)`   | Terminer phase validation                  | `Lobby`              |

**Validations** :

- `start_game()` : Vérifie min_players et max_players
- `start_round()` : Vérifie que le pool de missions est suffisant

---

### LobbyCommandService

**Fichier** : `backend/app/services/lobby_command_service.py`

**Responsabilités** :

- ✅ Opérations de modification sur les lobbies (CQRS - Command)
- ✅ Gestion des joueurs (inscription/désinscription)

**Dépendances** :

- `LobbyRepository`
- `PlayerRepository`

**Méthodes principales** :

| Méthode                                            | Description                          | Retour           |
| -------------------------------------------------- | ------------------------------------ | ---------------- |
| `create_lobby(lobby_data, host_id)`                | Créer un nouveau lobby               | `Lobby`          |
| `register_player(user_id, lobby_id, alias, color)` | Inscrire un utilisateur comme joueur | `Player`         |
| `unregister_player(lobby_id, user_id)`             | Désinscrire un joueur                | `Player \| None` |

---

### LobbyQueryService

**Fichier** : `backend/app/services/lobby_query_service.py`

**Responsabilités** :

- ✅ Opérations de lecture sur les lobbies (CQRS - Query)
- ✅ Construction de l'état d'un lobby

**Dépendances** :

- `LobbyRepository`
- `PlayerRepository`

**Méthodes principales** :

| Méthode                                | Description                                | Retour                |
| -------------------------------------- | ------------------------------------------ | --------------------- |
| `get_lobby(lobby_id)`                  | Obtenir un lobby par son ID                | `Lobby \| None`       |
| `get_players_by_lobby(lobby_id)`       | Liste des joueurs d'un lobby               | `list[Player]`        |
| `get_player_status(user_id, lobby_id)` | Statut d'un utilisateur (PLAYER/SPECTATOR) | `PlayerStatus`        |
| `build_lobby_state(lobby_id)`          | État complet du lobby (WebSocket)          | `WebSocketLobbyState` |
| `get_lobby_host_id(lobby_id)`          | ID de l'hôte du lobby                      | `UUID`                |

---

### SuggestionService

**Fichier** : `backend/app/services/suggestion_service.py`

**Responsabilités** :

- ✅ Gestion des suggestions temporaires (missions/rôles)
- ✅ Validation et promotion des suggestions en missions

**Stockage** : En mémoire (peut être migré vers DB)

**Dépendances** :

- `MissionRepository` (pour promouvoir les suggestions)
- `LobbyRepository` (pour obtenir le game_id)

**Méthodes principales** :

| Méthode                                                                      | Description                          | Retour                   |
| ---------------------------------------------------------------------------- | ------------------------------------ | ------------------------ |
| `create_suggestion(lobby_id, user_id, title, type, description, difficulty)` | Créer une suggestion temporaire      | `TempSuggestion`         |
| `get_suggestion(suggestion_id)`                                              | Obtenir une suggestion par son ID    | `TempSuggestion \| None` |
| `get_suggestions_by_lobby(lobby_id, validated_only)`                         | Liste des suggestions d'un lobby     | `list[Dict]`             |
| `validate_suggestion(suggestion_id, accepted)`                               | Valider/rejeter une suggestion       | `Mission \| None`        |
| `promote_to_mission(suggestion_id)`                                          | Promouvoir une suggestion en mission | `Mission`                |
| `reject_suggestion(suggestion_id)`                                           | Rejeter une suggestion               | `None`                   |

---

### MissionPoolService

**Fichier** : `backend/app/services/mission_pool_service.py`

**Responsabilités** :

- ✅ Définition du pool de missions disponibles
- ✅ Filtrage des missions selon contraintes
- ✅ Combinaison de sources (jeu + suggestions)

**Dépendances** :

- `LobbyRepository`
- `MissionRepository`

**Méthodes principales** :

| Méthode                                                                       | Description                       | Retour                      |
| ----------------------------------------------------------------------------- | --------------------------------- | --------------------------- |
| `get_available_missions_pool(lobby_id, source, exclude_completed_for_player)` | Pool de missions disponibles      | `list[Mission]`             |
| `get_available_missions_for_players(lobby_id, player_ids, source)`            | Missions disponibles par joueur   | `dict[UUID, list[Mission]]` |
| `validate_pool_sufficient(lobby_id, required_count, source)`                  | Vérifier si le pool est suffisant | `bool`                      |

**Sources** :

- `GAME_ONLY` : Missions du jeu uniquement
- `SUGGESTIONS_ONLY` : Suggestions validées uniquement
- `BOTH` : Jeu + suggestions

---

### MissionSelectionService

**Fichier** : `backend/app/services/mission_selection_service.py`

**Responsabilités** :

- ✅ Wrapper autour de `MissionPoolService` pour implémenter l'interface
- ✅ Adaptation de l'interface existante vers la nouvelle architecture

**Dépendances** :

- `MissionPoolService`

**Méthodes principales** :

| Méthode                                   | Description                    | Retour             |
| ----------------------------------------- | ------------------------------ | ------------------ |
| `get_available_missions_pool(...)`        | Délègue à `MissionPoolService` | `list`             |
| `get_available_missions_for_players(...)` | Délègue à `MissionPoolService` | `dict[UUID, list]` |
| `validate_pool_sufficient(...)`           | Délègue à `MissionPoolService` | `bool`             |

**Note** : C'est un wrapper d'adaptation pour respecter l'interface existante.

---

### MissionAssignmentService

**Fichier** : `backend/app/services/mission_assignment_service.py`

**Responsabilités** :

- ✅ Attribution des missions aux joueurs
- ✅ Validation des contraintes (unicité, suffisance)
- ✅ Sauvegarde des assignations en base
- ✅ Mise à jour des statuts des missions assignées

**Dépendances** :

- `MissionPoolService` (pour obtenir le pool)
- `LobbyRepository`
- `RoundRepository`
- `PlayerRepository`
- `MissionRepository`

**Méthodes principales** :

| Méthode                                                    | Description                                       | Retour                                      |
| ---------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| `assign_missions(lobby_id, round_number, source)`          | Attribuer missions (une par joueur, sans doublon) | `dict[UUID, UUID]` (player_id → mission_id) |
| `set_assigned_mission_status(assigned_mission_id, result)` | Mettre à jour statut (success/fail)               | `dict` (statut mis à jour)                  |
| `get_assignments_by_round(lobby_id, round_number)`         | Assignations d'un round                           | `dict[UUID, UUID]`                          |
| `get_mission_details_for_distribution(mission_id)`         | Détails pour distribution WebSocket               | `dict` (mission details)                    |

**Contraintes** :

- Une mission par joueur
- Pas de doublon dans un même round
- Pool suffisant avant assignation

---

### RoundService

**Fichier** : `backend/app/services/round_service.py`

**Responsabilités** :

- ✅ Gestion du cycle de vie des rounds
- ✅ Vérification de l'état des rounds (validés ou non)

**Dépendances** :

- `RoundRepository`
- `LobbyRepository`
- `PlayerRepository`
- `MissionRepository`

**Méthodes principales** :

| Méthode                                      | Description                | Retour          |
| -------------------------------------------- | -------------------------- | --------------- |
| `get_current_round(lobby_id)`                | Round actif (RUNNING)      | `Round \| None` |
| `close_round(lobby_id)`                      | Fermer un round (FINISHED) | `Round`         |
| `is_current_round_fully_validated(lobby_id)` | Toutes missions validées ? | `bool`          |

---

### ScoreService

**Fichier** : `backend/app/services/score_service.py`

**Responsabilités** :

- ✅ Calcul des scores par round
- ✅ Calcul des scores finaux
- ✅ Persistance des scores dans la base

**Dépendances** :

- `RoundRepository`
- `LobbyRepository`
- `PlayerRepository`

**Méthodes principales** :

| Méthode                                                       | Description                 | Retour                        |
| ------------------------------------------------------------- | --------------------------- | ----------------------------- |
| `compute_round_scores(lobby_id, round_number)`                | Scores d'un round           | `dict` (scores par joueur)    |
| `compute_final_scores(lobby_id)`                              | Scores finaux (tous rounds) | `dict` (scores + leaderboard) |
| `persist_round_scores(lobby_id, round_number, round_results)` | Persister les scores        | `None`                        |

**Points** :

- Mission COMPLETED : 10 points
- Mission FAILED : 0 point
- Mission ACTIVE : 0 point (pas encore validée)

---

## Flux d'Orchestration Typiques

### Flux 1 : Rejoindre un Lobby

```
Client WebSocket (événement: join_lobby)
  ↓
socket_server.py
  ↓
LobbyCommandHandler.join_lobby()
  ├→ WebSocketManager.join_lobby() [Infrastructure]
  └→ WebSocketManager.broadcast("user_joined") [Notification]
```

### Flux 2 : Inscrire un Joueur

```
Client WebSocket (événement: register_player)
  ↓
socket_server.py
  ↓
LobbyCommandHandler.register_player()
  ├→ LobbyCommandService.register_player() [Logique métier]
  └→ WebSocketManager.broadcast("player_registered") [Notification]
```

### Flux 3 : Démarrer une Partie

```
Client WebSocket (événement: start_game)
  ↓
socket_server.py
  ↓
GameCommandHandler.start_game()
  ├→ PhaseService.start_game() [Logique métier]
  │   ├→ Validation min_players / max_players
  │   └→ Mise à jour status → RUNNING
  └→ WebSocketManager.broadcast("game_started") [Notification]
```

### Flux 4 : Créer une Suggestion

```
Client WebSocket (événement: send_suggestion)
  ↓
socket_server.py
  ↓
GameCommandHandler.send_suggestion()
  ├→ PhaseService.get_current_phase() [Vérification phase]
  ├→ SuggestionService.create_suggestion() [Logique métier]
  ├→ LobbyQueryService.get_lobby_host_id() [Récupération hôte]
  ├→ WebSocketManager.send_to(host_sid, "suggestion_received") [Notification hôte]
  └→ WebSocketManager.broadcast("lobby_state") [Mise à jour état]
```

### Flux 5 : Démarrer un Round avec Missions

```
Client WebSocket (événement: start_round)
  ↓
socket_server.py
  ↓
GameCommandHandler.start_round()
  ├→ PhaseService.get_current_status() [Vérification statut]
  ├→ LobbyQueryService.get_players_by_lobby() [Récupération joueurs]
  ├→ MissionSelectionService.validate_pool_sufficient() [Validation pool]
  ├→ PhaseService.start_round() [Création round + phase ROUND]
  ├→ MissionAssignmentService.assign_missions() [Attribution missions]
  │   ├→ MissionPoolService.get_available_missions_for_players()
  │   └→ Sauvegarde MissionAssigned en DB
  ├→ GameCommandHandler.distribute_missions() [Distribution privée]
  │   ├→ LobbyQueryService.get_players_by_lobby()
  │   ├→ MissionAssignmentService.get_mission_details_for_distribution()
  │   └→ WebSocketManager.send_to() [mission_assigned privé]
  └→ WebSocketManager.broadcast() [round_started, missions_distributed, lobby_state]
```

### Flux 6 : Valider une Mission (Hôte)

```
Client WebSocket (événement: host_validate_mission)
  ↓
socket_server.py
  ↓
GameCommandHandler.host_validate_mission()
  ├→ LobbyQueryService.get_lobby_host_id() [Vérification hôte]
  ├→ MissionAssignmentService.set_assigned_mission_status() [Mise à jour statut]
  ├→ WebSocketManager.broadcast("mission_result") [Notification]
  ├→ RoundService.is_current_round_fully_validated() [Vérification complétude]
  ├→ GameCommandHandler.finalize_round() [Si toutes validées]
  │   ├→ RoundService.close_round()
  │   ├→ ScoreService.compute_round_scores()
  │   ├→ ScoreService.persist_round_scores()
  │   └→ WebSocketManager.broadcast("round_finished", "scores_updated")
  └→ WebSocketManager.broadcast("lobby_state") [Mise à jour état]
```

### Flux 7 : Finaliser un Round

```
Client WebSocket (événement: finalize_round)
  ↓
socket_server.py
  ↓
GameCommandHandler.finalize_round()
  ├→ RoundService.get_current_round() [Vérification round actif]
  ├→ RoundService.close_round() [Fermeture round]
  ├→ ScoreService.compute_round_scores() [Calcul scores]
  ├→ ScoreService.persist_round_scores() [Persistance]
  └→ WebSocketManager.broadcast() [round_finished, scores_updated, lobby_state]
```

---

## Mapping des Événements WebSocket

### Événements Lobby

| Événement Client → Serveur | Handler               | Méthode               | Événements Serveur → Client |
| -------------------------- | --------------------- | --------------------- | --------------------------- |
| `join_lobby`               | `LobbyCommandHandler` | `join_lobby()`        | `user_joined`               |
| `register_player`          | `LobbyCommandHandler` | `register_player()`   | `player_registered`         |
| `unregister_player`        | `LobbyCommandHandler` | `unregister_player()` | `player_unregistered`       |
| `sync_lobby_state`         | `LobbyCommandHandler` | `sync_lobby_state()`  | `lobby_state`               |

### Événements Jeu

| Événement Client → Serveur | Handler              | Méthode                   | Événements Serveur → Client                                                        |
| -------------------------- | -------------------- | ------------------------- | ---------------------------------------------------------------------------------- |
| `start_game`               | `GameCommandHandler` | `start_game()`            | `game_started`                                                                     |
| `end_game`                 | `GameCommandHandler` | `end_game()`              | `game_finished`                                                                    |
| `start_game_phase`         | `GameCommandHandler` | `start_game_phase()`      | (interne)                                                                          |
| `send_suggestion`          | `GameCommandHandler` | `send_suggestion()`       | `suggestion_received` (hôte), `lobby_state`                                        |
| `validate_suggestion`      | `GameCommandHandler` | `validate_suggestion()`   | `suggestion_validated`, `lobby_state`                                              |
| `start_round`              | `GameCommandHandler` | `start_round()`           | `round_started`, `mission_assigned` (privé), `missions_distributed`, `lobby_state` |
| `finalize_round`           | `GameCommandHandler` | `finalize_round()`        | `round_finished`, `scores_updated`, `lobby_state`                                  |
| `host_validate_mission`    | `GameCommandHandler` | `host_validate_mission()` | `mission_result`, `lobby_state` (et `round_finished` si toutes validées)           |

---

## Tests

Voir [Tests Backend](./tests.md).
