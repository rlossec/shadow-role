# Tests pour les endpoints d'authentification

## Structure

Cette suite de tests est organisée par endpoint, avec un fichier dédié pour chaque route :

- `test_register.py` - POST `/auth/register`
- `test_login.py` - POST `/auth/jwt/login`
- `test_refresh.py` - POST `/auth/refresh`
- `test_activate_account.py` - POST `/auth/activate-account`
- `test_resend_activation.py` - POST `/auth/resend_activation`
- `test_request_reset_password.py` - POST `/auth/request-reset-password`
- `test_reset_password.py` - POST `/auth/reset-password`
- `helpers.py` - Payloads de base, constantes et utilitaires réutilisables

## Organisation des tests

Chaque fichier de test est organisé par code de statut HTTP avec des séparateurs clairs :

```python
# 200/201/202/204 - Success
@pytest.mark.asyncio
async def test_xxx_success(...):
    ...

# 400 - Bad Request
@pytest.mark.asyncio
async def test_xxx_bad_request(...):
    ...

# 422 - Unprocessable Entity (validation)
@pytest.mark.asyncio
async def test_xxx_validation_error(...):
    ...

# 401 - Unauthorized
@pytest.mark.asyncio
async def test_xxx_unauthorized(...):
    ...
```

## Payloads de base et helpers

Les payloads de base, constantes et helpers sont définis dans `helpers.py` :

### Payloads

- `get_base_register_payload(...)` - Pour créer un utilisateur
- `get_base_login_form_data(...)` - Pour le login (form-urlencoded)
- `get_base_login_headers()` - Headers pour le login
- `get_base_refresh_payload(refresh_token)` - Pour rafraîchir un token
- `get_base_account_activation_request_payload(email)` - Pour demander l'activation
- `get_base_account_activation_confirm_payload(user_id, token)` - Pour confirmer l'activation
- `get_base_password_reset_request_payload(email)` - Pour demander la réinitialisation
- `get_base_password_reset_confirm_payload(user_id, token, password)` - Pour confirmer la réinitialisation

### Helpers d'utilisateurs

- `create_active_user(auth_service, username, email, password)` - Crée un utilisateur actif
- `create_inactive_user(auth_service, username, email, password)` - Crée un utilisateur inactif

### Constantes

- `LOGIN_BAD_CREDENTIALS` - Message d'erreur pour identifiants incorrects
- `RESET_PASSWORD_BAD_TOKEN` - Message d'erreur pour token de réinitialisation invalide
- `ACCOUNT_ACTIVATION_BAD_TOKEN` - Message d'erreur pour token d'activation invalide
- `REGISTER_DUPLICATE_USERNAME` - Message d'erreur pour username dupliqué
- `REGISTER_DUPLICATE_EMAIL` - Message d'erreur pour email dupliqué

### Champs obligatoires

Des constantes listent les champs obligatoires pour chaque endpoint :

- `REGISTER_REQUIRED_FIELDS` - Champs obligatoires pour l'inscription
- `LOGIN_REQUIRED_FIELDS` - Champs obligatoires pour le login
- `REFRESH_REQUIRED_FIELDS` - Champs obligatoires pour le refresh
- Etc.

## Tests itératifs pour champs obligatoires

Pour les endpoints avec des champs obligatoires (comme POST `/auth/register` ou POST `/auth/jwt/login`), un test paramétré itère automatiquement sur tous les champs requis :

```python
@pytest.mark.parametrize("missing_field", REGISTER_REQUIRED_FIELDS)
async def test_register_missing_required_fields(..., missing_field):
    # Teste chaque champ obligatoire individuellement
```

## Exécution des tests

### Tous les tests d'authentification

```bash
uv run pytest tests/api/authentication/ -v
```

### Tests spécifiques

```bash
# Tous les tests d'inscription
uv run pytest tests/api/authentication/test_register.py -v

# Tous les tests de connexion
uv run pytest tests/api/authentication/test_login.py -v

# Un test spécifique
uv run pytest tests/api/authentication/test_register.py::test_register_success -v
uv run pytest tests/api/authentication/test_login.py::test_login_success_with_username -v
```

### Avec couverture de code

```bash
uv run pytest tests/api/authentication/ --cov=api.authentication --cov-report=html
```

## Couverture des tests

Chaque endpoint est testé pour :

### POST `/auth/register`
- ✅ Cas de succès (status 201)
- ✅ Validation des champs obligatoires (status 422)
- ✅ Validation des emails invalides (status 422)
- ✅ Validation des champs vides (status 422)
- ✅ Validation des mots de passe correspondants (status 422)
- ✅ Doublons username/email (status 400)

### POST `/auth/jwt/login`
- ✅ Cas de succès avec username (status 200)
- ✅ Cas de succès avec email (status 200)
- ✅ Mauvais identifiants (status 400)
- ✅ Utilisateur inexistant (status 400)
- ✅ Utilisateur inactif (status 400/401)
- ✅ Validation des champs obligatoires (status 422)
- ✅ Validation des champs vides (status 400)

### POST `/auth/refresh`
- ✅ Cas de succès (status 200)
- ✅ Rotation des tokens
- ✅ Réutilisation du refresh token (status 401)
- ✅ Token invalide (status 401)
- ✅ Utilisation d'un access token comme refresh (status 401)
- ✅ Révoquement après logout (status 401)

### POST `/auth/activate-account`
- ✅ Cas de succès (status 200)
- ✅ Token invalide (status 400)

### POST `/auth/resend_activation`
- ✅ Cas de succès (status 202)
- ✅ Email inconnu (status 202, pas de token)
- ✅ Utilisateur déjà actif (status 202, pas de token)

### POST `/auth/request-reset-password`
- ✅ Génération de token (status 202)

### POST `/auth/reset-password`
- ✅ Cas de succès (status 200/204)
- ✅ Token invalide (status 400)

## Notes importantes

1. **Base de données de test** : Les tests utilisent SQLite en mémoire, donc chaque test a une base de données propre.
2. **Isolation** : Chaque test est isolé et utilise une session de base de données séparée.
3. **Fixtures** : `client`, `db_session`, `auth_service` et `account_activation_manager` sont définies dans `tests/conftest.py`.
4. **Stratégie** : Les tests préparent généralement leurs données via `auth_service` puis consomment l'endpoint HTTP pour l'action à valider.
5. **Helpers réutilisables** : Utilisez les helpers de `helpers.py` pour éviter la duplication de code.

## Ajout de nouveaux tests

Pour ajouter un nouveau test :

1. Utilisez les payloads de base depuis `helpers.py`
2. Créez une fonction de test avec le préfixe `test_`
3. Utilisez `@pytest.mark.asyncio`
4. Organisez par code de statut avec des séparateurs `# <status code>`
5. Faites des assertions claires et précises

Exemple :

```python
# 200 - Success
@pytest.mark.asyncio
async def test_my_new_test(client, auth_service):
    payload = get_base_register_payload()
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
```
