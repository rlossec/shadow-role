# Tests d'authentification

Ce dossier contient les tests unitaires pour les endpoints d'authentification. Les données de préparation utilisent principalement la fixture `auth_service` (voir `tests/conftest.py`) afin de créer les utilisateurs directement via le service métier, puis chaque test cible l'endpoint HTTP concerné.

## Tests disponibles

### test_register.py

Tests pour l'endpoint `/auth/register` :

- ✅ `test_register_success` - Enregistrement réussi
- ✅ `test_register_duplicate_username` - Rejet d'un username dupliqué (via `auth_service`)
- ✅ `test_register_duplicate_email` - Rejet d'un email dupliqué (via `auth_service`)
- ✅ `test_register_invalid_email` - Rejet d'un email invalide
- ✅ `test_register_missing_fields` - Rejet si champs manquants
- ✅ `test_register_empty_fields` - Rejet si champs vides
- ✅ `test_register_weak_password` - Test avec mot de passe faible
- ✅ `test_register_special_characters_in_username` - Test avec caractères spéciaux

### test_login.py

Tests pour l'endpoint `/auth/jwt/login` :

- ✅ `test_login_success_with_username` - Connexion réussie avec username (setup via `auth_service`)
- ✅ `test_login_success_with_email` - Connexion réussie avec email
- ✅ `test_login_wrong_password` - Rejet avec mauvais mot de passe
- ✅ `test_login_nonexistent_user` - Rejet avec utilisateur inexistant (username)
- ✅ `test_login_nonexistent_email` - Rejet avec utilisateur inexistant (email)
- ✅ `test_login_inactive_user` - Rejet avec utilisateur inactif (désactivation via SQLAlchemy)
- ✅ `test_login_missing_credentials` - Rejet si credentials manquants
- ✅ `test_login_empty_credentials` - Rejet si credentials vides
- ✅ `test_login_username_vs_email_same_value` - Test username/email identiques

### test_logout.py

Tests pour l'endpoint `/auth/jwt/logout` :

- ✅ `test_logout_success` - Logout avec token valide
- ✅ `test_logout_without_token_returns_401` - Logout protégé sans token

### test_request_reset_password.py

Tests pour l'endpoint `/auth/request-reset-password` :

- ✅ `test_request_reset_password_generates_token` - Génération d'un couple `(user_id, token)` de réinitialisation

### test_reset_password.py

Tests pour l'endpoint `/auth/reset-password` :

- ✅ `test_reset_password_success` - Réinitialisation avec `(user_id, token)` valide
- ✅ `test_reset_password_invalid_token` - Rejet d'un couple invalide

### test_resend_activation.py

Tests pour l'endpoint `/auth/resend_activation` :

- ✅ `test_resend_activation_success` - Génère `(user_id, token)` pour un compte inactif
- ✅ `test_resend_activation_unknown_email_returns_no_token` - Pas de fuite d'information si l’email est inconnu
- ✅ `test_resend_activation_user_already_active_returns_no_token` - Aucun token renvoyé si le compte est déjà actif

### test_activate_account.py

Tests pour l'endpoint `/auth/activate-account` :

- ✅ `test_activate_account_user_success` - Activation réussie avec `(user_id, token)` valide
- ✅ `test_activate_account_with_bad_token_returns_400` - Rejet d'un couple invalide

### test_refresh.py

Tests pour l'endpoint `/auth/refresh` :

- ✅ `test_refresh_success` - Génère un nouveau couple access/refresh
- ✅ `test_refresh_with_invalid_token_returns_401` - Rejette un refresh invalide
- ✅ `test_refresh_with_access_token_returns_401` - Refuse un access token passé en refresh

## Exécution des tests

### Tous les tests d'authentification

```bash
uv run pytest tests/api/authentication/ -v
```

### Tests spécifiques

```bash
# Tous les tests de register
uv run pytest tests/api/authentication/test_register.py -v

# Tous les tests de login
uv run pytest tests/api/authentication/test_login.py -v

# Un test spécifique
uv run pytest tests/api/authentication/test_register.py::test_register_success -v
uv run pytest tests/api/authentication/test_login.py::test_login_success_with_username -v
```

### Avec couverture de code

```bash
uv run pytest tests/api/authentication/ --cov=services.authentication --cov-report=html
```

## Notes importantes

1. **Base de données de test** : Les tests utilisent SQLite en mémoire, donc chaque test a une base de données propre.
2. **Isolation** : Chaque test est isolé et utilise une session de base de données séparée.
3. **Fixtures** : `client`, `db_session`, `auth_service` et `account_activation_manager` sont définies dans `tests/conftest.py`. `auth_service` encapsule `UserRepository` et `JWTRepository` avec la session de test.
4. **Stratégie** : Les tests préparent généralement leurs données via `auth_service` puis consomment l'endpoint HTTP pour l’action à valider.

## Structure des tests

Chaque test suit cette structure :

1. **Setup** : Création des données nécessaires (utilisateur, token, etc.) via fixtures/services.
2. **Action** : Appel à l'endpoint ciblé.
3. **Assertion** : Vérification des résultats attendus (status code, payload, état en base).

## Ajout de nouveaux tests

Pour ajouter un nouveau test :

1. Créez une fonction de test avec le préfixe `test_`.
2. Utilisez `@pytest.mark.asyncio`.
3. Utilisez les fixtures `client`, `db_session`, `auth_service` selon les besoins.
4. Faites des assertions claires et précises.

```python
@pytest.mark.asyncio
async def test_my_new_test(client, auth_service):
    await auth_service.register_user(...)
    response = await client.post(...)
    assert response.status_code == 200
```
