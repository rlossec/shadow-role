## Authentification JWT

### Workflow

1. Utilisateur se connecte via `/api/auth/login`
2. Backend vérifie ses identifiants
3. Backend génère un JWT avec payload : `{user_id, exp}`
4. Client envoie le JWT dans header : `Authorization: Bearer <token>`
5. Le token expire après 24h (configurable)

### Configuration

| Paramètre     | Valeur par défaut  |
| ------------- | ------------------ |
| Secret        | `JWT_SECRET` (env) |
| Algorithme    | HS256              |
| Expiration    | 24h (Access Token) |
| Refresh Token | 7 jours            |
