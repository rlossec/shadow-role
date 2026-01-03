# Sécurité - Shadow Role

Ce document décrit les mesures de sécurité implémentées dans Shadow Role.

## Authentification JWT

### Access Tokens et Refresh Tokens

Shadow Role utilise un système de tokens JWT avec deux types de tokens :

- **Access Token** : Token de courte durée (30 minutes par défaut) utilisé pour authentifier les requêtes API
- **Refresh Token** : Token de longue durée stocké dans une deny-list pour permettre la rotation des tokens

### Flux d'authentification

1. **Connexion** : `POST /api/auth/jwt/login`

   - Retourne un couple `access_token` + `refresh_token`
   - Le refresh token est stocké dans une deny-list

2. **Rafraîchissement** : `POST /api/auth/refresh`

   - Utilise le refresh token pour obtenir un nouveau couple
   - Le refresh token utilisé est invalidé (rotation)

3. **Déconnexion** : `POST /api/auth/jwt/logout`
   - Invalide le refresh token actuel

### Protection des routes

Les routes protégées utilisent le middleware `get_current_active_user` :

```python
@router.get("/me")
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    return current_user
```

Voir [Authentification Backend](../backend/authentication/README.md) pour plus de détails.

## WebSocket

### Authentification WebSocket

Les connexions WebSocket sont authentifiées via JWT lors du handshake :

```typescript
const socket = io("https://api.example.com", {
  path: "/ws/socket.io",
  auth: { token: localStorage.getItem("access_token") },
});
```

Le serveur valide le token avant d'accepter la connexion.

Voir [WebSocket Backend](../backend/websocket/README.md) pour plus de détails.

## Bonnes Pratiques

### Côté Backend

- ✅ Validation des données avec Pydantic
- ✅ Hashage des mots de passe avec Argon2
- ✅ Protection CSRF (via CORS configuré)
- ✅ Rate limiting (à implémenter)
- ✅ Logging des actions sensibles

### Côté Frontend

- ✅ Stockage sécurisé des tokens (localStorage)
- ✅ Refresh automatique des tokens
- ✅ Gestion des erreurs d'authentification
- ✅ Protection des routes avec guards

Voir [Authentification Frontend](./frontend/AUTH.md) pour plus de détails.

## Configuration

### Variables d'environnement sensibles

- `SECRET_KEY` : Clé secrète pour signer les JWT
- `DATABASE_URL` : URL de connexion à la base de données
- `SMTP_*` : Configuration email (si applicable)

⚠️ **Important** : Ne jamais commiter ces valeurs dans le dépôt Git.

## Évolutions Futures

- [ ] Rate limiting sur les endpoints sensibles
- [ ] 2FA (authentification à deux facteurs)
- [ ] Audit logging complet
- [ ] Chiffrement des données sensibles en base
