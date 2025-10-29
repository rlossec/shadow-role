## Authentification JWT

### Workflow

1. Utilisateur se connecte via `POST /auth/token` avec `username` et `password`
2. Backend vérifie ses identifiants
3. Backend génère un access token JWT avec payload : `{sub: user_id, exp}`
4. Client envoie le token dans header : `Authorization: Bearer <token>`
5. Quand le token expire, utiliser `POST /auth/refresh` avec l'ancien token pour en obtenir un nouveau

### Endpoints

- `POST /auth/token` - Connexion (obtient access token)
- `POST /auth/refresh` - Renouvellement du access token (utilise l'ancien token)
- `POST /auth/register` - Création de compte
- `GET /auth/me` - Profil utilisateur actuel (requiert authentification)

### Configuration

| Paramètre  | Valeur par défaut                                       |
| ---------- | ------------------------------------------------------- |
| Secret     | `SECRET_KEY` (env)                                      |
| Algorithme | HS256                                                   |
| Expiration | 30 min (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`) |

### Format des requêtes

Tous les endpoints d'authentification utilisent `application/x-www-form-urlencoded` :

- **Login** : `username=xxx&password=yyy`
- **Register** : `username=xxx&email=yyy@example.com&password=zzz`
- **Refresh** : `refresh_token=<access_token>`
