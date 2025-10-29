# Endpoints REST

### Authentification (`/auth`)

- `POST /auth/register` - Création de compte
- `POST /auth/token` - Connexion (obtient access token)
- `POST /auth/refresh` - Renouvellement du access token
- `GET /auth/me` - Profil utilisateur actuel

### Lobby (`/api/lobby`)

- `POST /api/lobby` - Créer un lobby
- `GET /api/lobby/{lobby_id}` - Détails d'un lobby
- `GET /api/lobby` - Liste des lobbies publics
- `POST /api/lobby/{lobby_id}/join` - Rejoindre un lobby
- `DELETE /api/lobby/{lobby_id}` - Quitter/Supprimer
- `POST /api/lobby/{lobby_id}/start` - Démarrer la partie

### Player (`/api/player`)

- `GET /api/player/{player_id}` - Détails d'un joueur
- `PUT /api/player/{player_id}` - Mettre à jour le statut
- `GET /api/player/{player_id}/role` - Rôle assigné (secret)
- `GET /api/player/{player_id}/mission` - Mission assignée (secret)

- `GET /api/player/lobby/{lobby_id}` - Joueurs du lobby

### Game (`/api/game`)

- `GET /api/game` - Liste des types de jeux
- `GET /api/game/{game_id}` - Détails d'un jeu
- `GET /api/game/{game_id}/roles` - Rôles disponibles
- `GET /api/game/{game_id}/missions` - Missions disponibles
