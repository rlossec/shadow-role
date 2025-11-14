# Référence API REST

Cette page centralise les endpoints principaux du backend FastAPI. Les payloads détaillés sont définis dans les schémas Pydantic (`backend/db/schemas/`).

### Endpoints

| Méthode | Endpoint                       | Description                                                             |
| ------- | ------------------------------ | ----------------------------------------------------------------------- |
| POST    | `/auth/register`               | Crée un utilisateur (inactif par défaut) et envoie l’email d’activation |
| POST    | `/auth/jwt/login`              | Authentifie et renvoie les jetons                                       |
| POST    | `/auth/jwt/logout`             | Invalide le refresh token soumis (déconnexion serveur)                  |
| POST    | `/auth/refresh`                | Régénère les jetons (rotation) et invalide le refresh token utilisé     |
| POST    | `/auth/activate-account`       | Active le compte (`is_active=True`) (`uid` + `token`)                   |
| POST    | `/auth/resend_activation`      | Renvoie un lien d’activation (`uid` + `token`)                          |
| POST    | `/auth/request-reset-password` | Envoie un lien de réinitialisation (`uid` + `token`)                    |
| POST    | `/auth/reset-password`         | Applique le nouveau mot de passe (`uid` + `token`)                      |
| GET     | `/auth/me`                     | Récupère l'utilisateur actif                                            |

**Configuration par défaut**

| Paramètre                     | Valeur                   |
| ----------------------------- | ------------------------ |
| `SECRET_KEY`                  | Variable d’environnement |
| `ALGORITHM`                   | `HS256`                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 minutes               |

## Game (`/api/games`)

| Méthode | Endpoint                        | Description                      |
| ------- | ------------------------------- | -------------------------------- |
| GET     | `/api/games`                    | Liste les jeux                   |
| POST    | `/api/games`                    | Créer un jeu                     |
| GET     | `/api/games/{game_id}`          | Détails d’un jeu                 |
| PUT     | `/api/games/{game_id}`          | Mettre un jeu à jour             |
| DELETE  | `/api/games/{game_id}`          | Supprimer un jeu                 |
| GET     | `/api/games/{game_id}/missions` | Missions disponibles pour ce jeu |

## Lobby (`/api/lobbies`)

| Méthode | Endpoint                          | Description                    |
| ------- | --------------------------------- | ------------------------------ |
| GET     | `/api/lobbies`                    | Liste des lobbies publics      |
| POST    | `/api/lobbies`                    | Crée un lobby                  |
| GET     | `/api/lobbies/{lobby_id}`         | Détails d’un lobby             |
| PUT     | `/api/lobbies/{lobby_id}`         | Mettre à jour un lobby         |
| DELETE  | `/api/lobbies/{lobby_id}`         | Supprimer un lobby             |
| POST    | `/api/lobbies/code/{code}`        | Récupère un lobby par son code |
| GET     | `/api/lobbies/{lobby_id}/players` | Liste des joueurs d’un lobby   |

## Player (`/api/players`)

| Méthode | Endpoint                            | Description                       |
| ------- | ----------------------------------- | --------------------------------- |
| GET     | `/api/players/{player_id}`          | Détails d’un joueur               |
| PUT     | `/api/players/{player_id}`          | Met à jour le statut d’un joueur  |
| DELETE  | `/api/players/{player_id}`          | Met à jour le statut d’un joueur  |
| GET     | `/api/players/{player_id}/missions` | Récupère les missions d'un joueur |

## Missions (`/api/missions`)

| Méthode | Endpoint                     | Description            |
| ------- | ---------------------------- | ---------------------- |
| POST    | `/api/missions/`             | Créer une mission      |
| GET     | `/api/missions/{mission_id}` | Détails d’une mission  |
| PUT     | `/api/missions/{mission_id}` | Met à jour une mission |
| DELETE  | `/api/missions/{mission_id}` | Supprimer une mission  |

### Actions en temps réel (WebSocket)

Certaines transitions de jeu sont pilotées via WebSocket (cf. `docs/backend/websocket_doc.md`). Les principaux événements attendus côté serveur :

| Événement client → serveur     | Description                                |
| ------------------------------ | ------------------------------------------ |
| `lobby:start_game`             | Démarre/reprend la partie                  |
| `lobby:pause_game`             | Met la partie en pause                     |
| `lobby:start_proposal_phase`   | Passe en phase de propositions             |
| `lobby:start_round`            | Lance une nouvelle manche                  |
| `lobby:start_validation_phase` | Débute la phase de validation              |
| `lobby:end_round`              | Termine la manche en cours                 |
| `lobby:end_game`               | Clôture la partie et calcule les résultats |

Les événements serveur → clients (`lobby_joined`, `game_update`, `mission_assigned`, etc.) sont listés dans la documentation WebSocket et permettent de mettre à jour l’UI temps réel (`LobbyProvider` côté frontend).
