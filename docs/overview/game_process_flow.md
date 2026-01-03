# Processus de Jeu - Flow Métier

Ce document décrit le processus complet d'une partie de jeu, en se concentrant sur la logique métier pure.

## Vue d'ensemble

Le processus de jeu se décompose en plusieurs phases :

1. **Préparation** : Création du jeu, missions, lobby
2. **Attente** : Les utilisateurs rejoignent et s'enregistrent comme joueurs
3. **Suggestion** : Les joueurs proposent des missions
4. **Sélection** : L'host choisit les missions disponibles
5. **Round** : Assignation et exécution des missions
6. **Validation** : Attribution des points
7. **Fin de round** : Clôture et préparation du round suivant

## 1. Préparation (REST API)

### 1.1 Création d'un Jeu

**Endpoint** : `POST /api/games`

**Responsable** : `GameRepository`

**Actions** :

- Créer un jeu avec ses métadonnées (nom, description, type, min/max joueurs)
- Le jeu est persistant et réutilisable

**État** : Jeu créé en base de données

### 1.2 Création de Missions pour un Jeu

**Endpoint** : `POST /api/games/{game_id}/missions`

**Responsable** : `MissionRepository`

**Actions** :

- Créer des missions associées au jeu
- Chaque mission a : titre, description, difficulté, type (mission/role), image_url
- Les missions sont persistantes et réutilisables

**État** : Missions créées et associées au jeu

### 1.3 Création d'un Lobby

**Endpoint** : `POST /api/lobbies`

**Responsable** : `LobbyCommandService.create_lobby()`

**Actions** :

- Créer un lobby avec un code unique
- Associer le lobby à un jeu existant
- L'utilisateur créateur devient automatiquement l'**host**
- Le lobby démarre en statut `WAITING`

**État** :

- Lobby créé avec `status = WAITING`, `phase = NONE`
- Host assigné
- Code unique généré

**Services impliqués** :

- `LobbyCommandService.create_lobby()`
- `LobbyRepository.create_lobby()`

## 2. Phase d'Attente

### 2.1 Rejoindre un Lobby

**WebSocket Event** : `join_lobby`

**Responsable** : `LobbyCommandHandler.join_lobby()`

**Actions** :

- Un utilisateur rejoint le lobby via WebSocket
- L'utilisateur est ajouté à la room WebSocket du lobby
- **Par défaut, l'utilisateur est un SPECTATOR**

**État** : Utilisateur connecté au lobby (spectator)

**Services impliqués** :

- `LobbyCommandHandler.join_lobby()` (orchestration + WebSocket)
- `WebSocketManager.join_lobby()` (WebSocket)

### 2.2 Gestion Joueur/Spectateur

**Actions miroirs** : Passer de `SPECTATOR` à `PLAYER` et inversement

#### 2.2.1 S'enregistrer comme Joueur

**WebSocket Event** : `register_player`

**Responsable** : `LobbyCommandHandler.register_player()`

**Actions** :

- Un utilisateur (spectator) s'enregistre comme joueur
- Création d'un `Player` avec alias et couleur
- L'utilisateur passe de `SPECTATOR` à `PLAYER`

**État** :

- `Player` créé avec `status = WAITING`

**Services impliqués** :

- `LobbyCommandService.register_player()` (logique métier)
- `LobbyCommandHandler.register_player()` (orchestration + WebSocket)
- `PlayerRepository.create_player()`

#### 2.2.2 Se désenregistrer comme Joueur

**WebSocket Event** : `unregister_player`

**Responsable** : `LobbyCommandHandler.unregister_player()`

**Actions** :

- Un joueur se désenregistre
- Le `Player` est supprimé
- L'utilisateur redevient `SPECTATOR`

**État** : `Player` supprimé, utilisateur redevient spectator

**Services impliqués** :

- `LobbyCommandService.unregister_player()` (logique métier)
- `LobbyCommandHandler.unregister_player()` (orchestration + WebSocket)
- `PlayerRepository.delete_player()`

**Contraintes communes** :

- Seulement si `lobby.status == WAITING`
- Pour `register_player` : respecter `min_players` et `max_players` du lobby

### 2.4 Démarrer la Partie

**WebSocket Event** : `start_game` (ou REST)

**Responsable** : `GameCommandHandler.start_game()`

**Actions** :

- Vérifier que le nombre de joueurs respecte `min_players` et `max_players`
- Changer le statut du lobby : `WAITING` → `RUNNING`
- Initialiser la phase : `phase = NONE`

**État** :

- `lobby.status = RUNNING`
- `lobby.phase = NONE`

**Services impliqués** :

- `GameCommandHandler.start_game()` (orchestration)
- `PhaseService.start_game()` (logique métier)
- `LobbyRepository.get_lobby()`
- `PlayerRepository.get_players_by_lobby()`

**Contraintes** :

- `lobby.status == WAITING`
- `len(players) >= lobby.min_players`
- `len(players) <= lobby.max_players`
- Seul l'host peut démarrer

## 3. Phase de Suggestion

### 3.1 Lancer la Phase de Suggestion

**WebSocket Event** : `start_suggestion` (via `start_game_phase`)

**Responsable** : `GameCommandHandler.start_game_phase()` + `PhaseService.start_suggestion_phase()`

**Actions** :

- Changer la phase : `phase = SUGGESTION`
- Les joueurs peuvent maintenant proposer des suggestions

**État** : `lobby.phase = SUGGESTION`

**Services impliqués** :

- `GameCommandHandler.start_game_phase()` (orchestration)
- `PhaseService.set_phase()` ou `PhaseService.start_suggestion_phase()` (logique métier)

**Contraintes** :

- `lobby.status == RUNNING`
- Seul l'host peut lancer

### 3.2 Proposer une Suggestion

**WebSocket Event** : `send_suggestion`

**Responsable** : `GameCommandHandler.send_suggestion()` + `SuggestionService.create_suggestion()`

**Actions** :

- Un joueur propose une suggestion (mission/role)
- La suggestion est **temporaire** (stockage en mémoire, pas persistée en BDD)
- La suggestion contient : titre, type, description, difficulté, `user_id`
- L'host est notifié (privé) de la nouvelle suggestion via WebSocket

**État** : Suggestion temporaire en mémoire (`TempSuggestion` dans `SuggestionService`)

**Services impliqués** :

- `GameCommandHandler.send_suggestion()` (orchestration + WebSocket)
- `SuggestionService.create_suggestion()` (logique métier, stockage en mémoire)

**Contraintes** :

- `lobby.phase == SUGGESTION`
- Seuls les joueurs peuvent proposer

**Note** : Les suggestions sont stockées en mémoire dans `SuggestionService._suggestions` (dictionnaire `{lobby_id: [TempSuggestion]}`).

### 3.3 Terminer la Phase de Suggestion

**WebSocket Event** : `end_suggestion` (via `start_game_phase` avec `phase = NONE`)

**Responsable** : `GameCommandHandler.start_game_phase()` + `PhaseService.end_suggestion_phase()`

**Actions** :

- Changer la phase : `phase = NONE`
- Les suggestions ne peuvent plus être proposées

**État** : `lobby.phase = NONE`

**Services impliqués** :

- `GameCommandHandler.start_game_phase()` (orchestration)
- `PhaseService.end_suggestion_phase()` (logique métier)

**Contraintes** :

- `lobby.phase == SUGGESTION`
- Seul l'host peut terminer

## 4. Phase de Sélection des Missions

### 4.1 Valider les Suggestions

**WebSocket Event** : `validate_suggestion`

**Responsable** : `GameCommandHandler.validate_suggestion()` + `SuggestionService.validate_suggestion()`

**Actions** :

L'host valide ou rejette chaque suggestion individuellement :

- Si acceptée : la suggestion est convertie en `Mission` persistée via `SuggestionService.promote_to_mission()`
- Si rejetée : la suggestion est supprimée du pool temporaire via `SuggestionService.reject_suggestion()`
- Les missions du jeu sont toujours disponibles dans le pool

**État** :

- Suggestions validées converties en `Mission` persistées
- Suggestions rejetées supprimées
- Pool disponible via `MissionPoolService` (recalculé à la volée)

**Services impliqués** :

- `GameCommandHandler.validate_suggestion()` (orchestration + WebSocket)
- `SuggestionService.validate_suggestion()` (logique métier)
- `SuggestionService.promote_to_mission()` (conversion suggestion → mission)
- `MissionRepository.create_mission()` (persistance)

**Contraintes** :

- Seul l'host peut valider
- Le pool doit être suffisant pour le nombre de joueurs (vérifié lors de `start_round`)

**Note** : Le pool `available_missions` est **recalculé à la volée** via `MissionPoolService.get_available_missions_pool()` en combinant :

- Les missions du jeu (`MissionSource.GAME_ONLY`)
- Les suggestions validées (converties en missions) (`MissionSource.BOTH` ou `MissionSource.SUGGESTIONS_ONLY`)

---

## 5. Phase de Round

### 5.1 Lancer un Round

**WebSocket Event** : `start_round`

**Responsable** : `GameCommandHandler.start_round()` (orchestration complète)

**Actions** :

1. Vérifier que le pool de missions est suffisant via `MissionSelectionService.validate_pool_sufficient()`
2. Créer un nouveau `Round` avec `round_number` incrémenté via `PhaseService.start_round_phase()`
3. Assigner une mission unique à chaque joueur via `MissionAssignmentService.assign_missions()`
4. Distribuer les missions aux joueurs via `GameCommandHandler.distribute_missions()` (WebSocket privé)
5. Changer la phase : `phase = ROUND` (fait par `PhaseService.start_round_phase()`)

**État** :

- `Round` créé avec `round_number` incrémenté
- `MissionAssigned` créées pour chaque joueur (statut `ACTIVE`)
- `lobby.phase = ROUND`
- Missions distribuées aux joueurs via WebSocket

**Services impliqués** :

- `GameCommandHandler.start_round()` (orchestration complète)
- `PhaseService.start_round_phase()` (création du round + changement de phase)
- `MissionSelectionService.validate_pool_sufficient()` (vérification du pool)
- `MissionAssignmentService.assign_missions()` (assignation des missions)
- `MissionPoolService.get_available_missions_for_players()` (récupération du pool par joueur)
- `RoundRepository.create_round()` (via PhaseService)
- `MissionRepository.assign_mission_to_player()` (via MissionAssignmentService)

**Contraintes** :

- `lobby.status == RUNNING`
- Pool de missions suffisant (vérifié avant création du round)
- Seul l'host peut lancer

**Résultat** :

- Dictionnaire `{player_id: mission_id}` des assignations
- Chaque joueur a une mission unique
- Broadcast WebSocket `round_started` (sans révéler les missions privées)

---

### 5.2 Distribution des Missions (WebSocket)

**Responsable** : `GameCommandHandler.distribute_missions()`

**Actions** :

- Chaque joueur reçoit les missions qu'il peut connaitre.
- Broadcast général `missions_distributed` (sans révéler les missions privées)

**Services impliqués** :

- `GameCommandHandler.distribute_missions()` (orchestration + WebSocket)
- `MissionAssignmentService.get_mission_details_for_distribution()` (détails de la mission)
- `WebSocketManager.send_to()` (envoi privé)
- `WebSocketManager.broadcast()` (broadcast général)

---

### 5.3 Exécution du Round

**Durée** : Le jeu se déroule à l'oral, **aucune action code n'est nécessaire**

**État** : `lobby.phase = ROUND`, les joueurs jouent

**Note** : Cette phase est purement humaine. Le code n'intervient pas.

---

### 5.4 Terminer le Round (Passage à la Validation)

**WebSocket Event** : `start_validation` (via `start_game_phase` avec `phase = VALIDATION`)

**Responsable** : `GameCommandHandler.start_game_phase()` + `PhaseService.start_validation_phase()`

**Actions** :

- Changer la phase : `phase = VALIDATION`
- Les missions peuvent maintenant être validées par l'host

**État** : `lobby.phase = VALIDATION`

**Services impliqués** :

- `GameCommandHandler.start_game_phase()` (orchestration)
- `PhaseService.start_validation_phase()` (logique métier)

**Contraintes** :

- `lobby.phase == ROUND`
- Seul l'host peut terminer

## 6. Phase de Validation

### 6.1 Valider les Missions

**WebSocket Event** : `host_validate_mission`

**Responsable** : `GameCommandHandler.host_validate_mission()` + `MissionAssignmentService.set_assigned_mission_status()`

**Actions** :

- L'host décide du résultat pour chaque mission assignée (une par une)
- Pour chaque `MissionAssigned` :
  - `status = COMPLETED` ou `FAILED` (via `MissionAssignmentService.set_assigned_mission_status()`)
  - `completed_at` est défini
  - Broadcast WebSocket `mission_result` pour informer tous les joueurs
- Si toutes les missions du round sont validées, le round est automatiquement finalisé via `finalize_round()`

**État** :

- `MissionAssigned.status` mis à jour (`COMPLETED` ou `FAILED`)
- `MissionAssigned.completed_at` défini
- Si toutes validées : round finalisé automatiquement

**Services impliqués** :

- `GameCommandHandler.host_validate_mission()` (orchestration + WebSocket)
- `MissionAssignmentService.set_assigned_mission_status()` (logique métier)
- `RoundService.is_current_round_fully_validated()` (vérification si toutes validées)
- `GameCommandHandler.finalize_round()` (si toutes validées)

**Contraintes** :

- `lobby.phase == VALIDATION`
- Seul l'host peut valider

---

### 6.2 Finaliser le Round

**WebSocket Event** : `finalize_round` (automatique quand toutes les missions sont validées, ou manuel)

**Responsable** : `GameCommandHandler.finalize_round()` (orchestration complète)

**Actions** :

1. Fermer le round actuel via `RoundService.close_round()` (`status = FINISHED`, `ended_at = now`)
2. Calculer les scores du round via `ScoreService.compute_round_scores()`
3. Persister les scores via `ScoreService.persist_round_scores()` (mise à jour `Player.score`)
4. Changer la phase : `phase = NONE` (via `PhaseService.end_validation_phase()` si nécessaire)
5. Broadcast WebSocket `round_finished` avec les résultats
6. Broadcast WebSocket `scores_updated` avec les scores

**État** :

- `Round.status = FINISHED`
- `Round.ended_at` défini
- `Player.score` mis à jour pour chaque joueur
- `lobby.phase = NONE`
- Round terminé

**Services impliqués** :

- `GameCommandHandler.finalize_round()` (orchestration complète)
- `RoundService.close_round()` (fermeture du round)
- `ScoreService.compute_round_scores()` (calcul des scores)
- `ScoreService.persist_round_scores()` (persistance des scores)
- `PhaseService.end_validation_phase()` (retour à phase NONE, si nécessaire)
- `RoundRepository` (via RoundService)
- `PlayerRepository` (mise à jour des scores, via ScoreService)

**Contraintes** :

- Toutes les missions du round doivent être validées (`COMPLETED` ou `FAILED`)
- Seul l'host peut finaliser (ou automatique si toutes validées)

**Résultat** :

- Scores calculés et persistés
- Round fermé
- Préparation pour le round suivant (si applicable)

---

## 7. Gestion de l'Historique

### 7.1 Missions Déjà Effectuées

**Concept** : Éviter de réassigner les mêmes missions à un joueur

**Implémentation** :

- Utiliser `MissionAssigned` avec `status = COMPLETED` ou `FAILED`
- `MissionPoolService.get_available_missions_for_players()` exclut les missions déjà complétées pour chaque joueur
- Chaque joueur a son propre pool de missions disponibles (excluant ses missions complétées)
- Permet d'éviter de réassigner les mêmes missions à un joueur

**Services impliqués** :

- `MissionRepository.get_available_missions()` (exclut les complétées)
- `MissionPoolService.get_available_missions_for_players()` (pool personnalisé par joueur)
- `MissionAssignmentService.assign_missions()` (utilise cette logique)

---

## Diagramme de Flow

```
[WAITING]
    │
    ├─→ register_player() → [Player créé]
    │
    ├─→ unregister_player() → [Player supprimé]
    │
    └─→ start_game() → [RUNNING, phase=NONE]
            │
            ├─→ start_suggestion_phase() → [phase=SUGGESTION]
            │       │
            │       ├─→ send_suggestion() → [Suggestion temporaire en mémoire]
            │       │
            │       └─→ end_suggestion_phase() → [phase=NONE]
            │
            ├─→ validate_suggestion() → [Suggestion → Mission persistée]
            │
            ├─→ start_round() → [Round créé, missions assignées, phase=ROUND]
            │       │
            │       ├─→ assign_missions() → [Missions assignées]
            │       │
            │       └─→ distribute_missions() → [WebSocket: missions envoyées privées]
            │
            ├─→ [JEU ORAL - Aucune action code]
            │
            ├─→ start_validation_phase() → [phase=VALIDATION]
            │       │
            │       ├─→ host_validate_mission() → [MissionAssigned mis à jour (COMPLETED/FAILED)]
            │       │
            │       └─→ finalize_round() → [Scores calculés, round fermé, phase=NONE]
            │
            └─→ [Retour à start_round() pour round suivant]
```

## États et Transitions

### Statut du Lobby (`lobby.status`)

```
WAITING → RUNNING → PAUSED → RUNNING → ENDED
```

### Phase du Lobby (`lobby.phase`)

```
NONE → SUGGESTION → NONE → ROUND → VALIDATION → NONE
```

### Statut du Joueur (`player.status`)

```
WAITING → PLAYING → COMPLETED/LEFT
```

### Statut de la Mission Assignée (`mission_assigned.status`)

```
ACTIVE → COMPLETED/FAILED/CANCELLED
```
