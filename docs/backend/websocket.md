## WebSocket (`/ws`)

### Endpoint principal

#### Endpoint

- `Socket.IO /ws/game/lobby/{lobby_id}` - Canal temps réel par lobby

#### Authentification Socket.IO

- Le JWT REST est transmis dans le handshake :

```ts
const socket = io("https://api.shadowrole.io", {
  auth: { token: localStorage.getItem("jwt") },
});
```

- Côté serveur, le middleware vérifie le token avant d’accepter la connexion :

```python
@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    await sio.save_session(sid, payload)
```

### Messages WebSocket

#### Messages client -> serveur

| Événement          | Description                |
| ------------------ | -------------------------- |
| `player_joined`    | Un joueur rejoint le lobby |
| `player_left`      | Un joueur quitte           |
| `game_started`     | Début du jeu               |
| `role_assigned`    | Rôle secret attribué       |
| `mission_assigned` | Mission attribuée          |
| `game_update`      | État général mis à jour    |
| `timer_update`     | Timer envoyé à tous        |
| `game_ended`       | Fin de partie              |

#### Messages client -> serveur

| Événement          | Description                           |
| ------------------ | ------------------------------------- |
| `join_lobby`       | Rejoint un lobby                      |
| `update_status`    | Change son état (prêt, inactif, etc.) |
| `complete_mission` | Indique une mission accomplie         |
| `ping`             | Keep-alive                            |

#### Exemple de communication WebSocket

```json
// Client → Serveur
{
  "type": "join_lobby",
  "lobby_id": "uuid"
}

// Serveur → Tous les clients du lobby
{
  "type": "player_joined",
  "player": { "id": "uuid", "username": "Alice" },
  "timestamp": "2025-10-25T12:00:00Z"
}
```
