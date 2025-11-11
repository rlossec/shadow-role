# Référence API REST

Cette page centralise les endpoints principaux du backend FastAPI. Les payloads détaillés sont définis dans les schémas Pydantic (`backend/db/schemas/`).

## Authentification (`/auth`)

### Workflow

1. **Inscription** : `POST /auth/register` crée un utilisateur inactif **et** déclenche immédiatement l’envoi d’un email d’activation contenant un lien signé.
2. **Confirmation par email** : l’utilisateur suit le lien reçu (token signé) pour appeler `POST /auth/activate-account` et activer son compte.
3. **Connexion** : `POST /auth/jwt/login` retourne un couple `access_token` / `refresh_token` (compte actif requis).
4. **Refresh token** : `POST /auth/refresh` régénère un **nouveau** couple de jetons et invalide immédiatement le refresh token présenté.
5. **Requêtes protégées** : ajouter l’en-tête `Authorization: Bearer <access_token>`.

### Autres endpoints utiles :

- `POST /auth/resend_activation` renvoie l'email d'activation (si le compte est encore inactif).
  **Gestion mot de passe** :
  - `POST /auth/request-reset-password` envoie un lien de réinitialisation par mail.
  - `POST /auth/reset-password` applique le changement avec le jeton fourni.

### Endpoints

| Méthode | Endpoint                       | Description                                                             |
| ------- | ------------------------------ | ----------------------------------------------------------------------- |
| POST    | `/auth/register`               | Crée un utilisateur (inactif par défaut) et envoie l’email d’activation |
| POST    | `/auth/jwt/login`              | Authentifie et renvoie les jetons                                       |
| POST    | `/auth/jwt/logout`             | Invalide le refresh token soumis (déconnexion serveur)                  |
| POST    | `/auth/request-reset-password` | Envoie un lien de réinitialisation (`uid` + `token`)                    |
| POST    | `/auth/reset-password`         | Applique le nouveau mot de passe (`uid` + `token`)                      |
| POST    | `/auth/resend_activation`      | Renvoie un lien d’activation (`uid` + `token`)                          |
| POST    | `/auth/activate-account`       | Active le compte (`is_active=True`) (`uid` + `token`)                   |
| POST    | `/auth/refresh`                | Régénère les jetons (rotation) et invalide le refresh token utilisé     |

**Configuration par défaut**

| Paramètre                     | Valeur                   |
| ----------------------------- | ------------------------ |
| `SECRET_KEY`                  | Variable d’environnement |
| `ALGORITHM`                   | `HS256`                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 minutes               |

## Lobby (`/api/lobbies`)

| Méthode | Endpoint                        | Description                   |
| ------- | ------------------------------- | ----------------------------- |
| POST    | `/api/lobbies`                  | Crée un lobby                 |
| GET     | `/api/lobbies`                  | Liste des lobbies publics     |
| GET     | `/api/lobbies/{lobby_id}`       | Détails d’un lobby            |
| POST    | `/api/lobbies/{lobby_id}/join`  | Rejoindre un lobby            |
| POST    | `/api/lobbies/{lobby_id}/start` | Démarrer la partie (hôte)     |
| DELETE  | `/api/lobbies/{lobby_id}`       | Quitter ou supprimer un lobby |

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

Les événements serveur → clients (`lobby_joined`, `game_update`, `role_assigned`, etc.) sont listés dans la documentation WebSocket et permettent de mettre à jour l’UI temps réel (`LobbyProvider` côté frontend).

## Player (`/api/players`)

| Méthode | Endpoint                           | Description                              |
| ------- | ---------------------------------- | ---------------------------------------- |
| GET     | `/api/players/{player_id}`         | Détails d’un joueur                      |
| PUT     | `/api/players/{player_id}`         | Met à jour le statut d’un joueur         |
| GET     | `/api/players/{player_id}/role`    | Récupère le rôle assigné (restreint)     |
| GET     | `/api/players/{player_id}/mission` | Récupère la mission assignée (restreint) |
| GET     | `/api/players/lobby/{lobby_id}`    | Liste des joueurs d’un lobby             |

## Game (`/api/games`)

| Méthode | Endpoint                        | Description                      |
| ------- | ------------------------------- | -------------------------------- |
| GET     | `/api/games`                    | Liste des types de jeux          |
| GET     | `/api/games/{game_id}`          | Détails d’un jeu                 |
| GET     | `/api/games/{game_id}/roles`    | Rôles disponibles pour ce jeu    |
| GET     | `/api/games/{game_id}/missions` | Missions disponibles pour ce jeu |
