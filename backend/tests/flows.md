# Flux de Jeu

Ce document décrit les différents flux de jeu pour comprendre le fonctionnement étape par étape.

## Flux de Démarrage de Partie

1. **Créer un lobby** → `LobbyService.create_lobby()`
2. **Inscrire des joueurs** → `LobbyService.register_player()`
3. **Démarrer la partie** → `GameSessionService.start_game_session()`
   - Vérifie les préconditions (assez de joueurs)
   - Change le statut à RUNNING via `PhaseService`
   - Retourne l'état de la session

## Flux de Suggestion

1. **Phase SUGGESTION** → `PhaseService.start_suggestion_phase()`
2. **Créer une suggestion** → `GameSessionService.create_suggestion()`
3. **Valider la suggestion** → `GameSessionService.validate_suggestion()`
   - Si acceptée : devient une mission
   - Si rejetée : supprimée

## Flux de Round

1. **Démarrer un round** → `GameSessionService.start_round_with_missions()`
   - Valide le pool de missions
   - Crée un round via `PhaseService`
   - Attribue les missions via `MissionAssignmentService`
2. **Valider les missions** → `GameSessionService.validate_mission_result()`
3. **Finaliser le round** → `GameSessionService.finalize_round()`
   - Ferme le round via `RoundService`
   - Calcule les scores via `ScoreService`
   - Persiste les scores

## Phases du jeu

### Phase Pending

État "attente d'action" : le jeu est prêt, mais aucune phase n'est en cours.

- `status = "running"`
- `phase = "pending"`

### Phase Suggestion

Phase où les joueurs proposent de nouveaux rôles ou missions.

- `status = "running"`
- `phase = "suggestion"`

### Phase Round

Lancement d'un round = répartition des rôles et missions.

- `status = "running"`
- `phase = "round"`

### Phase Validation

Une fois le round joué, l'admin valide les résultats.

- `status = "running"`
- `phase = "validation"`
