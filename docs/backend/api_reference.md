# Référence API REST

Cette page centralise les endpoints principaux du backend FastAPI.

## Configuration par défaut

| Paramètre                     | Valeur                   |
| ----------------------------- | ------------------------ |
| `SECRET_KEY`                  | Variable d’environnement |
| `ALGORITHM`                   | `HS256`                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 minutes               |

## Authentication (`/api/auth`)

| Méthode | Endpoint                       | Nom de route             | Codé | Description                                                             |
| ------- | ------------------------------ | ------------------------ | ---- | ----------------------------------------------------------------------- |
| POST    | `/auth/register`               | `register`               | ✅   | Crée un utilisateur (inactif par défaut) et envoie l’email d’activation |
| POST    | `/auth/jwt/login`              | `login`                  | ✅   | Authentifie et renvoie les jetons                                       |
| POST    | `/auth/jwt/logout`             | `logout`                 | ✅   | Invalide le refresh token soumis (déconnexion serveur)                  |
| POST    | `/auth/refresh`                | `refresh_token`          | ✅   | Régénère les jetons (rotation) et invalide le refresh token utilisé     |
| POST    | `/auth/activate-account`       | `activate_account`       | ✅   | Active le compte (`is_active=True`) (`uid` + `token`)                   |
| POST    | `/auth/resend_activation`      | `resend_activation`      | ✅   | Renvoie un lien d’activation (`uid` + `token`)                          |
| POST    | `/auth/request-reset-password` | `request_reset_password` | ✅   | Envoie un lien de réinitialisation (`uid` + `token`)                    |
| POST    | `/auth/reset-password`         | `reset_password`         | ✅   | Applique le nouveau mot de passe (`uid` + `token`)                      |
| GET     | `/auth/me`                     | `get_current_user`       | ✅   | Récupère l'utilisateur actif                                            |

## Game (`/api/games`)

| Méthode | Endpoint                        | Nom de route        | Codé | Description                      |
| ------- | ------------------------------- | ------------------- | ---- | -------------------------------- |
| GET     | `/api/games`                    | `list_games`        | ✅   | Liste les jeux                   |
| POST    | `/api/games`                    | `create_game`       | ✅   | Créer un jeu                     |
| GET     | `/api/games/{game_id}`          | `get_game`          | ✅   | Détails d’un jeu                 |
| PUT     | `/api/games/{game_id}`          | `update_game`       | ✅   | Mettre un jeu à jour             |
| DELETE  | `/api/games/{game_id}`          | `delete_game`       | ✅   | Supprimer un jeu                 |
| GET     | `/api/games/{game_id}/missions` | `get_game_missions` | ✅   | Missions disponibles pour ce jeu |

## Lobby (`/api/lobbies`)

| Méthode | Endpoint                   | Nom de route        | Codé | Description                    |
| ------- | -------------------------- | ------------------- | ---- | ------------------------------ |
| GET     | `/api/lobbies`             | `list_lobbies`      | ✅   | Liste des lobbies publics      |
| POST    | `/api/lobbies`             | `create_lobby`      | ✅   | Crée un lobby                  |
| GET     | `/api/lobbies/{lobby_id}`  | `get_lobby`         | ✅   | Détails d’un lobby             |
| PUT     | `/api/lobbies/{lobby_id}`  | `update_lobby`      | ✅   | Mettre à jour un lobby         |
| DELETE  | `/api/lobbies/{lobby_id}`  | `delete_lobby`      | ✅   | Supprimer un lobby             |
| GET     | `/api/lobbies/code/{code}` | `get_lobby_by_code` | ✅   | Récupère un lobby par son code |

**Note** : L'endpoint pour lister les joueurs d'un lobby est disponible via `/api/players/lobby/{lobby_id}` (voir section Player).

## Player (`/api/players`)

| Méthode | Endpoint                           | Nom de route          | Codé | Description                       |
| ------- | ---------------------------------- | --------------------- | ---- | --------------------------------- |
| GET     | `/api/players/{player_id}`         | `get_player`          | ✅   | Détails d’un joueur               |
| PUT     | `/api/players/{player_id}`         | `update_player`       | ✅   | Met à jour le statut d’un joueur  |
| GET     | `/api/players/{player_id}/mission` | `get_player_missions` | ✅   | Récupère les missions d'un joueur |
| GET     | `/api/players/lobby/{lobby_id}`    | `get_lobby_players`   | ✅   | Liste des joueurs d’un lobby      |

## Missions (`/api/missions`)

| Méthode | Endpoint                       | Nom de route           | Codé | Description            |
| ------- | ------------------------------ | ---------------------- | ---- | ---------------------- |
| POST    | `/api/missions`                | `create_mission`       | ✅   | Créer une mission      |
| GET     | `/api/missions/{mission_id}`   | `get_mission`          | ✅   | Détails d’une mission  |
| PUT     | `/api/missions/{mission_id}`   | `update_mission`       | ✅   | Met à jour une mission |
| DELETE  | `/api/missions/{mission_id}`   | `delete_mission`       | ✅   | Supprimer une mission  |
| GET     | `/api/missions/game/{game_id}` | `get_missions_by_game` | ✅   | Missions d'un jeu      |
