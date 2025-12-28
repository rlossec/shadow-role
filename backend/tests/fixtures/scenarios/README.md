# Scénarios de Test

Ce répertoire contient les fixtures de scénarios organisées par catégorie pour créer des situations de test réutilisables.

## Structure

```
scenarios/
├── users.py           # Fixtures pour les utilisateurs
├── game.py            # Fixtures pour les jeux et missions
├── lobby.py           # Fixtures pour les lobbies et joueurs
├── game_session.py    # Scénarios complets de session de jeu
└── __init__.py        # Exports publics
```

## Organisation par Fichier

### Utilisateurs

Fichiers : `users.py`
Fixtures pour créer des comptes utilisateurs de différents types.

#### `setup_users`

Crée plusieurs comptes utilisateurs.

**Paramètres** :

- `count` (int, optionnel) : Nombre d'utilisateurs à créer (par défaut: 5)

**Retourne** :

- `list[User]` : Liste des utilisateurs créés

**Usage** :

```python
async def test_something(setup_users):
    users = setup_users  # 5 utilisateurs par défaut
    # ou
    users = await setup_users(count=10)  # 10 utilisateurs
```

#### `setup_admin_user`

Crée un compte utilisateur administrateur.

**Retourne** :

- `User` : Utilisateur administrateur avec `is_superuser=True`

**Usage** :

```python
async def test_admin_feature(setup_admin_user):
    admin = setup_admin_user
    # ...
```

---

### Jeux et Missions

Fichier : `game.py`
Fixtures pour créer des jeux avec leurs missions associées.

#### `setup_game_with_missions`

Crée un jeu avec plusieurs missions.

**Paramètres** :

- `count` (int, optionnel) : Nombre de missions à créer (par défaut: 5)

**Retourne** :

```python
{
    "game": Game,
    "game_missions": list[Mission]  # Missions du jeu
}
```

**Usage** :

```python
async def test_game_feature(setup_game_with_missions):
    game = setup_game_with_missions["game"]
    missions = setup_game_with_missions["game_missions"]
    # ...
```

---

### Lobbies et Joueurs

Fichier : `lobby.py`
Fixtures pour créer des lobbies avec ou sans joueurs.

#### `setup_lobby`

Crée un lobby avec un hôte. Nécessite `setup_game_with_missions`.

**Retourne** :

```python
{
    "lobby": Lobby,
    "game": Game,
    "game_missions": list[Mission],
    "host": User
}
```

**Usage** :

```python
async def test_lobby_feature(setup_lobby):
    lobby = setup_lobby["lobby"]
    host = setup_lobby["host"]
    # ...
```

#### `setup_lobby_with_players`

Crée un lobby complet avec des joueurs. Nécessite `setup_lobby` et `setup_users`.

**Paramètres** :

- `count` (int, optionnel) : Nombre de joueurs à créer (par défaut: 3)

**Retourne** :

```python
{
    "lobby": Lobby,
    "game": Game,
    "game_missions": list[Mission],
    "host": User,
    "users": list[User],      # Utilisateurs des joueurs
    "players": list[Player]   # Joueurs du lobby
}
```

**Usage** :

```python
async def test_lobby_with_players(setup_lobby_with_players):
    scenario = setup_lobby_with_players
    lobby = scenario["lobby"]
    players = scenario["players"]
    # ...
```

---

### Scénarios Complets

Fichier : `game_session.py`
Fixtures pour créer des scénarios complets et complexes utilisés pour tester les handlers et services.

#### `setup_game_session_scenario`

Crée un scénario complet pour tester les handlers et services de jeu.

**Retourne** :

```python
{
    "host": User,
    "game": Game,
    "missions": list[Mission],  # 5 missions
    "lobby": Lobby,
    "players": list[Player],    # 2 joueurs
    "users": list[User]         # Utilisateurs des joueurs
}
```

**Usage** :

```python
async def test_game_handler(setup_game_session_scenario):
    scenario = setup_game_session_scenario
    lobby = scenario["lobby"]
    players = scenario["players"]
    missions = scenario["missions"]
    # ...
```

## Découverte Automatique

Toutes les fixtures sont automatiquement disponibles dans tous les tests grâce à `conftest.py`. Vous n'avez pas besoin de les importer explicitement :

```python
# ✅ Fonctionne automatiquement
async def test_my_feature(setup_lobby_with_players):
    # ...
```

## Combinaison de Fixtures

Les fixtures peuvent être combinées pour créer des scénarios plus complexes :

```python
async def test_complex_scenario(
    setup_lobby_with_players,
    setup_admin_user
):
    lobby_scenario = setup_lobby_with_players
    admin = setup_admin_user
    # ...
```

## Ajouter un Nouveau Scénario

1. **Déterminez la catégorie** : Utilisateurs, Jeu, Lobby, ou Session complète
2. **Ajoutez la fixture** dans le fichier approprié
3. **Exportez-la** dans `__init__.py`
4. **Documentez-la** dans ce README

**Exemple** :

```python
# scenarios/lobby.py
@pytest.fixture
async def setup_lobby_with_many_players(db_session, setup_lobby, setup_users, count=10):
    """Crée un lobby avec beaucoup de joueurs."""
    # ... votre logique
    return {...}

# scenarios/__init__.py
from tests.fixtures.scenarios.lobby import (
    setup_lobby,
    setup_lobby_with_players,
    setup_lobby_with_many_players,  # Nouveau
)
```
