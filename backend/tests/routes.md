# Utilisation des noms de route

Tous les endpoints sont accessibles via leur nom de route avec FastAPI `url_path_for()` pour le reverse lookup.

## Exemple d'utilisation

```python
from main import app

# Générer une URL depuis le nom de la route
url = app.url_path_for("get_lobby", lobby_id="123e4567-e89b-12d3-a456-426614174000")
# Résultat: /api/lobbies/123e4567-e89b-12d3-a456-426614174000

url = app.url_path_for("list_lobbies")
# Résultat: /api/lobbies
```

## Avantages

Cela permet de modifier les chemins des routes dans le code sans avoir à mettre à jour les URLs en dur dans les tests ou ailleurs.

## Utilisation dans les tests

Dans vos tests, utilisez toujours `url_path_for()` plutôt que des URLs en dur :

```python
from main import app

async def test_get_lobby(client):
    lobby_id = "123e4567-e89b-12d3-a456-426614174000"
    url = app.url_path_for("get_lobby", lobby_id=lobby_id)
    response = await client.get(url)
    assert response.status_code == 200
```
