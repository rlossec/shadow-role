# ⚙️ 1. **Lancement / Création du lobby**

```
POST /api/lobbies
Content-Type: application/json
{
  "name": "Soirée du samedi",
  "host_name": "Ronan",
  "color": "#33AAFF",
  "game_id": 3              // optionnel, référence à un set de missions/roles prédéfini
}

```

### 🔸 Backend actions

- Crée un `Lobby` en base.
- Initialise `status = "waiting"` et `game_state = null`.
- Retourne `{ lobby_id, token, host_id }`.

### 🔸 Front

- Redirige vers `/lobby/{lobby_id}`.
- Établit la connexion WebSocket :

# ⚙️ 2. Phase — **Game Pending**

> L’état pending est un état “attente d’action” : le jeu est prêt, mais aucune phase n’est en cours.

### 🔸 Statut global

```json
{
  "status": "running",
  "phase": "pending"
}
```

### 🔸 WebSocket Events

| Event              | Direction        | Payload                                                   | Description                     |
| ------------------ | ---------------- | --------------------------------------------------------- | ------------------------------- |
| `start_game`       | client host → WS | `{ lobby_id }`                                            | L’hôte démarre la partie        |
| `game_started`     | WS → tous        | `{ status: "running", phase: "pending", players: [...] }` | Notification du début           |
| `start_suggestion` | client host → WS | `{ lobby_id }`                                            | Démarre une phase de suggestion |
| `start_round`      | client host → WS | `{ lobby_id }`                                            | Démarre une phase de round      |
| `pause_game`       | client host → WS | `{}`                                                      | Met en pause                    |
| `resume_game`      | client host → WS | `{}`                                                      | Reprend après pause             |

# 💡 3. Phase — **Suggestion**

> Phase où les joueurs proposent de nouveaux rôles ou missions.
>
> `status = "running"`
>
> `phase = "suggestion"`

### 🔸 Début

| Event               | Direction        | Payload                                     |
| ------------------- | ---------------- | ------------------------------------------- |
| `start_suggestion`  | client host → WS | `{ lobby_id }`                              |
| `suggestion_opened` | WS → tous        | `{ phase: "suggestion", can_submit: true }` |

---

### 🔸 Envoi de propositions

| Event              | Direction   | Payload                                                                    |
| ------------------ | ----------- | -------------------------------------------------------------------------- |
| `new_suggestion`   | client → WS | `{ title, description, type: "role"                                        |
| `suggestion_added` | WS→ tous    | `{ suggestions: [ { id, title, type, from_user, is_validated: false } ] }` |

> Le backend stocke ces propositions dans missions ou roles selon type, is_validated = false.

---

### 🔸 Fin de la phase

| Event               | Direction      | Payload                                    |
| ------------------- | -------------- | ------------------------------------------ |
| `end_suggestion`    | host → serveur | `{}`                                       |
| `suggestion_closed` | serveur → tous | `{ phase: "pending", suggestions: [...] }` |

**Effet backend :**

- Marque la phase comme close.
- `status` reste `running`, `phase` devient `pending`.
- Optionnellement, `validated = false` pour toutes les suggestions en attente.

# 🎯 4. Phase — **Round**

> Lancement d’un round = répartition des rôles et missions.
>
> `status = "running"`
>
> `phase = "round"`

### 🔸 Démarrage

| Event              | Direction          | Payload                                                                           | Description                |
| ------------------ | ------------------ | --------------------------------------------------------------------------------- | -------------------------- |
| `start_round`      | client host → WS   | `{ lobby_id, use_game_id?: boolean }`                                             | Démarre un nouveau round   |
| `round_started`    | WS → tous          | `{ phase: "round", players: [...], public_roles: [...], public_missions: [...] }` | Diffusé à tous les joueurs |
| `role_assigned`    | WS → joueur unique | `{ role_id, name, description }`                                                  | Message privé              |
| `mission_assigned` | WS→ joueur unique  | `{ mission_id, name, description }`                                               | Message privé              |

**Backend :**

- Sélectionne les missions/roles :
  - Si `game_id` présent → peut piocher dans la base associée.
  - Sinon → prend dans les propositions validées.
- Assigne aléatoirement les rôles / missions.
- Stocke dans `game_state.current_round`.

---

# ✅ 5. Phase — **Validation (Check)**

> Une fois le round joué, l’admin valide les résultats.

### 🔸 Début de validation

| Event           | Direction      | Payload                   |
| --------------- | -------------- | ------------------------- |
| `start_check`   | host → serveur | `{ lobby_id }`            |
| `check_started` | serveur → tous | `{ phase: "validation" }` |

---

### 🔸 Fin de validation

| Event         | Direction      | Payload                                               |
| ------------- | -------------- | ----------------------------------------------------- |
| `end_round`   | host → serveur | `{ results: [ { player_id, mission_id, success } ] }` |
| `round_ended` | serveur → tous | `{ results, scores, phase: "pending" }`               |

**Backend :**

- Calcule les scores.
- Met à jour les missions/roles validées.
- Sauvegarde les résultats du round dans la DB.
- Passe `phase` → `pending`.

# 🏁 6. Fin de la partie

| Event        | Direction      | Payload                                                   | Description                |
| ------------ | -------------- | --------------------------------------------------------- | -------------------------- |
| `end_game`   | host → serveur | `{}`                                                      | L’hôte met fin à la partie |
| `game_ended` | serveur → tous | `{ status: "ended", summary: { scores, rounds_played } }` | Résumé final diffusé       |
