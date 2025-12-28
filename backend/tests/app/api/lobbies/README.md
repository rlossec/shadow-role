# Tests pour les endpoints /api/lobbies

## Structure

Cette suite de tests est organisée par endpoint, avec un fichier dédié pour chaque route :

- `test_create_lobby.py` - POST `/api/lobbies`
- `test_get_lobby.py` - GET `/api/lobbies/{lobby_id}`
- `test_list_lobbies.py` - GET `/api/lobbies`
- `test_update_lobby.py` - PUT `/api/lobbies/{lobby_id}`
- `test_delete_lobby.py` - DELETE `/api/lobbies/{lobby_id}`
- `test_get_lobby_by_code.py` - GET `/api/lobbies/code/{code}`
- `helpers.py` - Payloads de base et utilitaires réutilisables

## Organisation des tests

Chaque fichier de test est organisé par code de statut HTTP avec des séparateurs clairs :

```python
# 200 - Success
@pytest.mark.asyncio
async def test_xxx_success(...):
    ...

# 400/422 - Bad Request / Unprocessable Entity
@pytest.mark.asyncio
async def test_xxx_validation_error(...):
    ...

# 404 - Not Found
@pytest.mark.asyncio
async def test_xxx_not_found(...):
    ...

# 403 - Forbidden
@pytest.mark.asyncio
async def test_xxx_forbidden(...):
    ...

# 401 - Unauthorized
@pytest.mark.asyncio
async def test_xxx_unauthorized(...):
    ...
```

## URLs et payloads de base

Les URLs et payloads de base sont définis dans `helpers.py` :

### URLs (via FastAPI reverse lookup)

Les URLs sont générées automatiquement via FastAPI `url_path_for()` depuis les noms des routes :

- `get_lobbies_url()` - URL pour lister les lobbies (GET `/api/lobbies`)
- `get_create_lobby_url()` - URL pour créer un lobby (POST `/api/lobbies`)
- `get_lobby_url(lobby_id)` - URL pour récupérer un lobby (GET `/api/lobbies/{lobby_id}`)
- `get_update_lobby_url(lobby_id)` - URL pour mettre à jour un lobby (PUT `/api/lobbies/{lobby_id}`)
- `get_delete_lobby_url(lobby_id)` - URL pour supprimer un lobby (DELETE `/api/lobbies/{lobby_id}`)
- `get_lobby_by_code_url(code)` - URL pour récupérer un lobby par code (GET `/api/lobbies/code/{code}`)

**Avantage** : Les URLs sont générées automatiquement depuis les noms des routes FastAPI. Si les routes changent (prefix, path, etc.), les URLs dans les tests s'adaptent automatiquement sans modification !

### Payloads

- `get_base_lobby_create_payload(game_id: str)` - Pour créer un lobby
- `get_base_lobby_update_payload(game_id: str = None)` - Pour mettre à jour un lobby

## Tests itératifs pour champs obligatoires

Pour les endpoints avec des champs obligatoires (comme POST `/api/lobbies`), un test paramétré itère automatiquement sur tous les champs requis :

```python
@pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
async def test_create_lobby_missing_required_fields(..., missing_field):
    # Teste chaque champ obligatoire individuellement
```

## Exécution des tests

Exécuter tous les tests des lobbies :

```bash
uv run pytest tests/api/lobbies/ -v
```

Exécuter un fichier spécifique :

```bash
uv run pytest tests/api/lobbies/test_create_lobby.py -v
```

Exécuter un test spécifique :

```bash
uv run pytest tests/api/lobbies/test_create_lobby.py::test_create_lobby_success -v
```

## Couverture des tests

Chaque endpoint est testé pour :

- ✅ Cas de succès (status 200/201/204)
- ✅ Validation des champs obligatoires (status 422)
- ✅ Ressource non trouvée (status 404)
- ✅ Permissions insuffisantes (status 403)
- ✅ Authentification requise (status 401)
- ✅ UUID invalide (status 422)
- ✅ Mise à jour partielle (pour PUT)
