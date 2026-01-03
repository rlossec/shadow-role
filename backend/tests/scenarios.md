# Scénarios de Test

Ce document décrit les scénarios de test pour valider le fonctionnement complet du système.

## 📋 Vue d'ensemble

Les scénarios de test couvrent les flux complets de jeu depuis la création du lobby jusqu'à la fin de la partie, en utilisant des connexions WebSocket authentifiées par JWT.

## 🎯 Scénario "Qui suis je" (E2E)

### Objectif

Valider le flux complet d'une partie de jeu avec :

- Authentification WebSocket via JWT (sans passer par REST)
- Gestion des connexions multiples
- Phase de suggestion
- Validation des suggestions
- Attribution et validation des missions
- Finalisation de la partie

### Prérequis

- Un jeu "Qui suis je" préexistant avec **8 missions/rôles**
- 4 joueurs : Alice (hôte), Bob, Chloé, David

### Étapes du test

#### 1. Création du lobby (API REST)

**Action** : Alice crée un lobby via API REST

```python
POST /api/lobbies
{
    "name": "Test Lobby E2E",
    "game_id": "<game_qui_suis_je_id>",
    "min_players": 4,
    "max_players": 10
}
```

**Résultat attendu** :

- Lobby créé avec Alice comme hôte
- Status: `WAITING`
- Code de lobby généré

---

#### 2. Connexion WebSocket avec JWT

**Action** : Chaque joueur ouvre une connexion WebSocket avec son JWT

```python
# Pour chaque joueur (Alice, Bob, Chloé, David)
socket = socketio.AsyncClient()
await socket.connect(
    "http://localhost:8000",
    auth={"token": "<jwt_token>"},
    socketio_path="/ws/socket.io"
)
```

**Résultat attendu** :

- Connexion réussie pour chaque joueur
- Événement `connection_ready` reçu
- Utilisateur authentifié et enregistré

**Note** : Les JWT sont générés directement pour les tests sans passer par l'endpoint REST `/auth/jwt/login`.

---

#### 3. Rejoindre le lobby

**Action** : Chaque joueur envoie `join_lobby`

```python
await socket.emit("join_lobby", {
    "lobby_id": "<lobby_id>"
})
```

**Résultat attendu** :

- Événement `user_joined` broadcast à tous les joueurs du lobby
- Événement `lobby_state` avec l'état mis à jour
- Joueur ajouté à la room WebSocket du lobby

---

#### 4. Inscription des joueurs

**Action** : Chaque joueur s'inscrit comme player

```python
await socket.emit("register_player", {
    "lobby_id": "<lobby_id>",
    "alias": "Alice",
    "color": "#FF0000"
})
```

**Résultat attendu** :

- Événement `player_registered` broadcast
- Player créé en base de données
- État du lobby mis à jour

---

#### 5. Refresh de page (David)

**Action** : David refresh sa page (simulation de reconnexion)

```python
# Déconnexion
await david_socket.disconnect()

# Reconnexion
await david_socket.connect(...)
await david_socket.emit("join_lobby", {"lobby_id": "<lobby_id>"})
```

**Résultat attendu** :

- Reconnexion réussie
- Synchronisation de l'état du lobby
- Événement `state_sync` reçu

---

#### 6. Démarrage de la partie

**Action** : Alice démarre la partie

```python
await alice_socket.emit("start_game", {
    "lobby_id": "<lobby_id>"
})
```

**Résultat attendu** :

- Événement `game_started` broadcast à tous
- Status du lobby: `RUNNING`
- Phase: `NONE`

---

#### 7. Lancement de la phase de suggestion

**Action** : Alice lance la phase de suggestion

```python
# Via le service directement (pas d'événement WebSocket direct pour l'instant)
await phase_service.start_suggestion_phase(lobby_id)
```

**Résultat attendu** :

- Phase du lobby: `SUGGESTION`
- Événement `lobby_state` avec phase mise à jour
- Les joueurs peuvent maintenant proposer des suggestions

---

#### 8. Envoi de suggestions

**Action** : Bob et Chloé envoient une suggestion

```python
# Bob
await bob_socket.emit("send_suggestion", {
    "lobby_id": "<lobby_id>",
    "user_id": "<bob_user_id>",
    "title": "Mission secrète de Bob",
    "type": "mission",
    "description": "Une mission proposée par Bob",
    "difficulty": 50
})

# Chloé
await chloe_socket.emit("send_suggestion", {
    "lobby_id": "<lobby_id>",
    "user_id": "<chloe_user_id>",
    "title": "Rôle mystérieux de Chloé",
    "type": "role",
    "description": "Un rôle proposé par Chloé",
    "difficulty": 60
})
```

**Résultat attendu** :

- Événement `suggestion_received` envoyé à Alice (hôte)
- Suggestions créées en base de données
- État du lobby mis à jour avec le nombre de suggestions

---

#### 9. Validation des suggestions

**Action** : Alice valide les suggestions

```python
# Valider la suggestion de Bob
await alice_socket.emit("validate_suggestion", {
    "lobby_id": "<lobby_id>",
    "host_user_id": "<alice_user_id>",
    "temp_id": "<bob_suggestion_id>",
    "accepted": True
})

# Valider la suggestion de Chloé
await alice_socket.emit("validate_suggestion", {
    "lobby_id": "<lobby_id>",
    "host_user_id": "<alice_user_id>",
    "temp_id": "<chloe_suggestion_id>",
    "accepted": True
})
```

**Résultat attendu** :

- Événement `suggestion_validated` broadcast
- Suggestions acceptées converties en missions
- Missions ajoutées au pool disponible
- État du lobby mis à jour

---

#### 10. Sélection des missions et lancement du round

**Action** : Alice lance le round avec toutes les missions disponibles

```python
await alice_socket.emit("start_round", {
    "lobby_id": "<lobby_id>",
    "mission_source": "both"  # Game missions + suggestions
})
```

**Résultat attendu** :

- Round créé (round_number: 1)
- Missions attribuées aux joueurs
- Événement `round_started` broadcast
- Événement `mission_assigned` envoyé à chaque joueur (privé)
- Événement `missions_distributed` broadcast
- Phase: `ROUND`

**Pool de missions** :

- 8 missions du jeu "Qui suis je"
- 2 missions créées à partir des suggestions validées
- **Total : 10 missions disponibles**

---

#### 11. Clôture du round et passage en validation

**Action** : Alice clôt le round et passe en phase validation

```python
# Passer en phase validation
await phase_service.start_validation_phase(lobby_id)
```

**Résultat attendu** :

- Phase: `VALIDATION`
- Événement `lobby_state` avec phase mise à jour
- Les missions assignées sont prêtes à être validées

---

#### 12. Validation des missions

**Action** : Alice valide ou invalide le succès de chaque mission

```python
# Pour chaque mission assignée
await alice_socket.emit("host_validate_mission", {
    "lobby_id": "<lobby_id>",
    "host_user_id": "<alice_user_id>",
    "player_id": "<player_id>",
    "assigned_mission_id": "<assigned_mission_id>",
    "result": "success"  # ou "fail"
})
```

**Résultat attendu** :

- Événement `mission_result` broadcast pour chaque validation
- Statut de la mission assignée mis à jour
- Si toutes les missions sont validées, le round est automatiquement finalisé

---

#### 13. Finalisation du round

**Action** : Le round est finalisé automatiquement quand toutes les missions sont validées

**Résultat attendu** :

- Événement `round_finished` broadcast
- Événement `scores_updated` broadcast avec les scores du round
- Round status: `FINISHED`
- Scores calculés et mis à jour

---

#### 14. Fin de la partie

**Action** : Alice termine la partie

```python
await alice_socket.emit("end_game", {
    "lobby_id": "<lobby_id>"
})
```

**Résultat attendu** :

- Événement `game_finished` broadcast
- Scores finaux calculés et inclus dans l'événement
- Status du lobby: `ENDED`
- État final du lobby broadcast

---

## 🔧 Implémentation technique

### Structure du test

Le test E2E est implémenté dans :

```
backend/tests/app/websocket/e2e/test_e2e_qui_suis_je.py
```

### Helpers utilisés

#### Création de JWT

```python
from tests.app.websocket.helpers import create_jwt_token

token = create_jwt_token(user_id)
```

Crée un JWT directement sans passer par l'endpoint REST.

#### Création du jeu "Qui suis je"

```python
from tests.app.websocket.helpers import create_qui_suis_je_game

game_data = await create_qui_suis_je_game(
    db_session, game_repo, mission_repo, creator
)
```

Crée un jeu avec 8 missions/rôles prédéfinis.

### Client WebSocket de test

Une classe `WebSocketClient` est fournie pour faciliter les tests :

```python
class WebSocketClient:
    def __init__(self, token: str, user_id: UUID)
    async def connect(self, base_url: str)
    async def disconnect(self)
    async def emit(self, event: str, data: Dict[str, Any])
    def get_events(self, event_name: str) -> List[Dict[str, Any]]
    def wait_for_event(self, event_name: str, timeout: float) -> Dict[str, Any]
```

### Événements WebSocket testés

| Événement               | Direction   | Description              |
| ----------------------- | ----------- | ------------------------ |
| `connection_ready`      | WS → Client | Connexion établie        |
| `join_lobby`            | Client → WS | Rejoindre un lobby       |
| `user_joined`           | WS → Tous   | Un utilisateur a rejoint |
| `player_registered`     | WS → Tous   | Un joueur s'est inscrit  |
| `game_started`          | WS → Tous   | La partie a démarré      |
| `send_suggestion`       | Client → WS | Proposer une suggestion  |
| `suggestion_received`   | WS → Hôte   | Suggestion reçue (privé) |
| `validate_suggestion`   | Client → WS | Valider une suggestion   |
| `suggestion_validated`  | WS → Tous   | Suggestion validée       |
| `start_round`           | Client → WS | Démarrer un round        |
| `round_started`         | WS → Tous   | Round démarré            |
| `mission_assigned`      | WS → Joueur | Mission assignée (privé) |
| `host_validate_mission` | Client → WS | Valider une mission      |
| `mission_result`        | WS → Tous   | Résultat d'une mission   |
| `round_finished`        | WS → Tous   | Round terminé            |
| `scores_updated`        | WS → Tous   | Scores mis à jour        |
| `end_game`              | Client → WS | Terminer la partie       |
| `game_finished`         | WS → Tous   | Partie terminée          |

## 🚀 Exécution du test

```bash
# Exécuter le test E2E
uv run pytest tests/app/websocket/e2e/test_e2e_qui_suis_je.py -v -s

# Avec couverture
uv run pytest tests/app/websocket/e2e/test_e2e_qui_suis_je.py --cov=app.websocket --cov-report=html
```

## ✅ Critères de succès

Le test est considéré comme réussi si :

1. ✅ Tous les joueurs se connectent avec succès via WebSocket
2. ✅ Le lobby est créé et les joueurs peuvent le rejoindre
3. ✅ La partie démarre correctement
4. ✅ La phase de suggestion fonctionne (création et validation)
5. ✅ Le round démarre avec les missions attribuées
6. ✅ Les missions sont validées correctement
7. ✅ Le round est finalisé avec les scores calculés
8. ✅ La partie se termine avec les scores finaux
9. ✅ Tous les événements WebSocket attendus sont émis
10. ✅ L'état du lobby reste cohérent à chaque étape

## 📊 Données de test

### Jeu "Qui suis je"

Le jeu contient 8 missions/rôles :

1. **Le détective** - Découvrir qui est le meurtrier (difficulté: 50)
2. **Le meurtrier** - Éliminer tous les autres sans être découvert (difficulté: 60)
3. **Le témoin** - A vu le meurtrier mais personne ne vous croit (difficulté: 40)
4. **L'innocent** - Innocent mais suspecté par tous (difficulté: 30)
5. **Le complice** - Aide le meurtrier en secret (difficulté: 70)
6. **Le protecteur** - Protège l'innocent du meurtrier (difficulté: 50)
7. **Le médiateur** - Essaie de maintenir la paix (difficulté: 40)
8. **Le traître** - Change de camp selon la situation (difficulté: 80)

### Joueurs

- **Alice** : Hôte du lobby
- **Bob** : Joueur, propose une suggestion
- **Chloé** : Joueur, propose une suggestion
- **David** : Joueur, teste la reconnexion

## 🔍 Points d'attention

### Authentification WebSocket

Les JWT sont générés directement pour les tests, sans passer par l'endpoint REST. Cela permet de tester uniquement le flux WebSocket sans dépendre de l'API REST.

### Reconnexion

Le test simule une reconnexion (David refresh sa page) pour valider que :

- L'état du lobby est correctement synchronisé
- Les connexions multiples sont gérées
- Les rooms WebSocket sont correctement maintenues

### Distribution des missions

Les missions sont distribuées de manière privée à chaque joueur via l'événement `mission_assigned`. Le test vérifie que :

- Chaque joueur reçoit sa mission
- Les missions ne sont pas révélées aux autres joueurs
- L'événement `missions_distributed` est broadcast (sans révéler les détails)

### Validation automatique

Quand toutes les missions d'un round sont validées, le round est automatiquement finalisé. Le test vérifie ce comportement.

## 📝 Notes d'implémentation

### Limitations actuelles

1. **Test hybride** : Le test actuel utilise à la fois les services directement et les handlers WebSocket. Un vrai test E2E nécessiterait un serveur de test en cours d'exécution.

2. **Événement `start_suggestion`** : Il n'y a pas encore d'événement WebSocket direct pour démarrer la phase de suggestion. Le test utilise directement le service pour l'instant.

3. **Simulation WebSocket** : Pour un vrai test E2E, il faudrait utiliser `socketio.AsyncClient` avec un serveur de test réel.

### Améliorations futures

- [ ] Ajouter un événement WebSocket `start_suggestion`
- [ ] Créer un serveur de test pour les tests E2E réels
- [ ] Ajouter des tests de performance pour les connexions multiples
- [ ] Tester les cas d'erreur (déconnexion, timeout, etc.)

---

## 📋 Scénario Général - Phases du Jeu

### 1. Préalables

En amont, plusieurs choses sont créées :

- 4 utilisateurs qui créent leurs comptes : Alice, Bob, Chloé et David.
- un jeu "Qui suis je ?" avec des missions propres.

L'hôte Alice créé le lobby et le front utilise l'API REST :

**POST** `/api/lobbies`

```json
{
  "name": "Soirée du samedi",
  "game_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "min_players": 2,
  "max_players": 10
}
```

#### Backend actions

- Crée un `Lobby` en base.
- Initialise `status = "waiting"` et `game_state = null`.
- Retourne

```json
{
  "id": "3etyf6f-5717-4322-b3éc-2cT73f66afa6",
  "name": "string",
  "game_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "max_players": 10,
  "code": "string",
  "host_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "waiting",
  "current_players": 0,
  "created_at": "2025-11-12T13:31:48.315Z",
  "expires_at": "2025-11-12T13:31:48.315Z"
}
```

#### Front

- Redirige vers `/lobby/{lobby_id}`.
- Établit la connexion WebSocket.

---

### 2. Phase — Game Pending

> L'état pending est un état "attente d'action" : le jeu est prêt, mais aucune phase n'est en cours.

#### Statut global

```json
{
  "status": "running",
  "phase": "pending"
}
```

#### WebSocket Events

| Event              | Direction        | Payload                                                   | Description                     |
| ------------------ | ---------------- | --------------------------------------------------------- | ------------------------------- |
| `start_game`       | client host → WS | `{ lobby_id }`                                            | L'hôte démarre la partie        |
| `game_started`     | WS → tous        | `{ status: "running", phase: "pending", players: [...] }` | Notification du début           |
| `start_suggestion` | client host → WS | `{ lobby_id }`                                            | Démarre une phase de suggestion |
| `start_round`      | client host → WS | `{ lobby_id }`                                            | Démarre une phase de round      |
| `pause_game`       | client host → WS | `{}`                                                      | Met en pause                    |
| `resume_game`      | client host → WS | `{}`                                                      | Reprend après pause             |

---

### 3. Phase — Suggestion

> Phase où les joueurs proposent de nouveaux rôles ou missions.
>
> `status = "running"`
>
> `phase = "suggestion"`

#### Début

| Event               | Direction        | Payload                                     |
| ------------------- | ---------------- | ------------------------------------------- |
| `start_suggestion`  | client host → WS | `{ lobby_id }`                              |
| `suggestion_opened` | WS → tous        | `{ phase: "suggestion", can_submit: true }` |

---

#### Envoi de propositions

| Event              | Direction   | Payload                                                                    |
| ------------------ | ----------- | -------------------------------------------------------------------------- |
| `new_suggestion`   | client → WS | `{ title, description, type: "role" }`                                     |
| `suggestion_added` | WS → tous   | `{ suggestions: [ { id, title, type, from_user, is_validated: false } ] }` |

> Le backend stocke ces propositions dans missions is_validated = false.

---

#### Fin de la phase

| Event               | Direction      | Payload                                    |
| ------------------- | -------------- | ------------------------------------------ |
| `end_suggestion`    | host → serveur | `{}`                                       |
| `suggestion_closed` | serveur → tous | `{ phase: "pending", suggestions: [...] }` |

**Effet backend :**

- Marque la phase comme close.
- `status` reste `running`, `phase` devient `pending`.
- Optionnellement, `validated = false` pour toutes les suggestions en attente.

---

### 4. Phase — Round

> Lancement d'un round = répartition des rôles et missions.
>
> `status = "running"`
>
> `phase = "round"`

#### Démarrage

| Event              | Direction          | Payload                                                      | Description                |
| ------------------ | ------------------ | ------------------------------------------------------------ | -------------------------- |
| `start_round`      | client host → WS   | `{ lobby_id, use_game_id?: boolean }`                        | Démarre un nouveau round   |
| `round_started`    | WS → tous          | `{ phase: "round", players: [...], public_missions: [...] }` | Diffusé à tous les joueurs |
| `mission_assigned` | WS → joueur unique | `{ mission_id, name, description }`                          | Message privé              |

**Backend :**

- Sélectionne les missions :
  - Si `game_id` présent → peut piocher dans la base associée.
  - Sinon → prend dans les propositions validées.
- Assigne aléatoirement les rôles / missions.
- Stocke dans `game_state.current_round`.

---

### 5. Phase — Validation (Check)

> Une fois le round joué, l'admin valide les résultats.

#### Début de validation

| Event           | Direction      | Payload                   |
| --------------- | -------------- | ------------------------- |
| `start_check`   | host → serveur | `{ lobby_id }`            |
| `check_started` | serveur → tous | `{ phase: "validation" }` |

---

#### Fin de validation

| Event         | Direction      | Payload                                               |
| ------------- | -------------- | ----------------------------------------------------- |
| `end_round`   | host → serveur | `{ results: [ { player_id, mission_id, success } ] }` |
| `round_ended` | serveur → tous | `{ results, scores, phase: "pending" }`               |

**Backend :**

- Calcule les scores.
- Met à jour les missions validées.
- Sauvegarde les résultats du round dans la DB.
- Passe `phase` → `pending`.

---

### 6. Fin de la partie

| Event        | Direction      | Payload                                                   | Description                |
| ------------ | -------------- | --------------------------------------------------------- | -------------------------- |
| `end_game`   | host → serveur | `{}`                                                      | L'hôte met fin à la partie |
| `game_ended` | serveur → tous | `{ status: "ended", summary: { scores, rounds_played } }` | Résumé final diffusé       |
