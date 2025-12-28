# Factories pour les tests

Ce répertoire contient des factories basées sur `factory-boy` pour créer facilement des données de test avec SQLAlchemy async.

## Architecture

Toutes les factories héritent de `BaseFactory` qui adapte `factory-boy` pour fonctionner avec SQLAlchemy async. La session de base de données est configurée automatiquement via `conftest.py`.

## Installation

Les factories utilisent `factory-boy` qui est inclus dans les dépendances de développement (`pyproject.toml`).

## Configuration automatique

Les factories sont automatiquement configurées avec la session de test dans `conftest.py`. Vous n'avez **pas besoin** de les configurer manuellement dans vos tests.

## Utilisation

### Import des factories

```python
from tests.factories import (
    UserFactory,
    GameFactory,
    LobbyFactory,
    PlayerFactory,
    MissionFactory,
    RoundFactory,
    MissionAssignedFactory,
    TagFactory,
)
```

### Créer des objets en base de données

Utilisez la méthode `create()` pour créer et sauvegarder un objet en base de données :

```python
# Créer un utilisateur avec les valeurs par défaut
user = await UserFactory.create()

# Créer un utilisateur avec des attributs personnalisés
user = await UserFactory.create(
    username="john_doe",
    email="john@example.com",
    is_active=True
)

# Créer un jeu
game = await GameFactory.create(
    name="Mon Jeu",
    game_type=GameTypeEnum.MISSION,
    min_players=3,
    max_players=6
)
```

### Relations automatiques avec SubFactory

Les factories utilisent `SubFactory` pour créer automatiquement les objets liés :

```python
# Créer un lobby - crée automatiquement un Game et un User (host)
lobby = await LobbyFactory.create()

# Créer un joueur - crée automatiquement un Lobby et un User
player = await PlayerFactory.create()

# Créer une mission - crée automatiquement un Game et un User (creator)
mission = await MissionFactory.create()
```

Vous pouvez aussi surcharger les relations :

```python
# Créer un lobby avec un jeu spécifique
game = await GameFactory.create(name="Mon Jeu")
lobby = await LobbyFactory.create(game=game)  # Utilise le jeu existant

# Créer un joueur avec un lobby et un utilisateur spécifiques
user = await UserFactory.create(username="player1")
lobby = await LobbyFactory.create()
player = await PlayerFactory.create(lobby=lobby, user=user)
```

### Construire des objets sans les sauvegarder

Utilisez la méthode `build()` pour créer un objet sans le sauvegarder en base de données :

```python
# Construire un utilisateur sans le sauvegarder
user = UserFactory.build(username="test_user")

# Construire un jeu sans le sauvegarder
game = GameFactory.build(name="Test Game")
```

**Note** : `build()` ne crée pas automatiquement les objets liés via `SubFactory`. Vous devrez les fournir manuellement ou utiliser `build()` sur chaque factory.

## Exemples complets

### Exemple 1 : Création simple

```python
@pytest.mark.asyncio
async def test_example(db_session):
    # Créer un utilisateur
    user = await UserFactory.create(username="testuser")

    # Créer un jeu
    game = await GameFactory.create(name="Test Game")

    # Créer un lobby avec le jeu et l'utilisateur
    lobby = await LobbyFactory.create(game=game, host=user)

    # Créer un joueur
    player = await PlayerFactory.create(lobby=lobby, user=user)

    assert player.lobby_id == lobby.id
    assert player.user_id == user.id
```

### Exemple 2 : Utilisation des SubFactory automatiques

```python
@pytest.mark.asyncio
async def test_automatic_relations(db_session):
    # Créer un lobby - crée automatiquement un Game et un User (host)
    lobby = await LobbyFactory.create()

    # Le lobby a automatiquement un game et un host
    assert lobby.game is not None
    assert lobby.host is not None

    # Créer un joueur - crée automatiquement un Lobby et un User
    player = await PlayerFactory.create()

    # Le joueur a automatiquement un lobby et un user
    assert player.lobby is not None
    assert player.user is not None
```

### Exemple 3 : Création avec attributs personnalisés

```python
@pytest.mark.asyncio
async def test_custom_attributes(db_session):
    # Créer un utilisateur avec des attributs spécifiques
    user = await UserFactory.create(
        username="john_doe",
        email="john@example.com",
        is_active=True,
        is_superuser=False
    )

    # Créer un jeu avec des paramètres spécifiques
    game = await GameFactory.create(
        name="Mon Super Jeu",
        description="Un jeu fantastique",
        game_type=GameTypeEnum.MISSION,
        min_players=3,
        max_players=6
    )

    # Créer un lobby avec le jeu et l'utilisateur
    lobby = await LobbyFactory.create(
        game=game,
        host=user,
        name="Mon Lobby",
        min_players=2,
        max_players=6
    )
```

### Exemple 4 : Scénario complet avec missions

```python
@pytest.mark.asyncio
async def test_complete_scenario(db_session):
    # Créer un hôte
    host = await UserFactory.create(username="host")

    # Créer un jeu
    game = await GameFactory.create(
        name="Mission Game",
        game_type=GameTypeEnum.MISSION
    )

    # Créer des missions
    missions = []
    for i in range(3):
        mission = await MissionFactory.create(
            game=game,
            title=f"Mission {i+1}",
            difficulty=50 + i * 10
        )
        missions.append(mission)

    # Créer un lobby
    lobby = await LobbyFactory.create(
        game=game,
        host=host,
        name="Mon Lobby"
    )

    # Créer des joueurs
    players = []
    for i in range(3):
        user = await UserFactory.create(username=f"player{i}")
        player = await PlayerFactory.create(
            lobby=lobby,
            user=user,
            status=PlayerStatus.PLAYING,
            score=i * 10
        )
        players.append(player)

    # Créer un round
    round_obj = await RoundFactory.create(
        lobby=lobby,
        round_number=1
    )

    # Assigner des missions aux joueurs
    for i, player in enumerate(players):
        await MissionAssignedFactory.create(
            player=player,
            mission=missions[i]
        )
```

## Factories disponibles

### UserFactory

Crée des utilisateurs de test.

**Champs par défaut :**

- `email`: `user{n}@example.com` (séquence)
- `username`: `user{n}` (séquence)
- `hashed_password`: `"hashed-password"`
- `is_active`: `True`
- `is_superuser`: `False`

**Exemple :**

```python
user = await UserFactory.create(username="john", email="john@example.com")
```

### GameFactory

Crée des jeux de test.

**Champs par défaut :**

- `name`: `"Game {n}"` (séquence)
- `description`: `"A test game"`
- `min_players`: `2`
- `max_players`: `10`
- `game_type`: `GameTypeEnum.MISSION`
- `tags`: Crée automatiquement un tag

**Exemple :**

```python
game = await GameFactory.create(name="Mon Jeu", game_type=GameTypeEnum.ROLE)
```

### LobbyFactory

Crée des lobbies de test.

**Champs par défaut :**

- `name`: `"Lobby {n}"` (séquence)
- `code`: `"CODE{n}"` (séquence)
- `status`: `LobbyStatus.WAITING`
- `phase`: `LobbyPhase.NONE`
- `game`: Crée automatiquement un `Game` (SubFactory)
- `host`: Crée automatiquement un `User` (SubFactory)

**Exemple :**

```python
lobby = await LobbyFactory.create(name="Mon Lobby")
```

### PlayerFactory

Crée des joueurs de test.

**Champs par défaut :**

- `status`: `PlayerStatus.WAITING`
- `score`: `0`
- `lobby`: Crée automatiquement un `Lobby` (SubFactory)
- `user`: Crée automatiquement un `User` (SubFactory)

**Exemple :**

```python
player = await PlayerFactory.create(status=PlayerStatus.PLAYING, score=100)
```

### MissionFactory

Crée des missions de test.

**Champs par défaut :**

- `title`: `"Mission {n}"` (séquence)
- `description`: `"Do something"`
- `difficulty`: `50`
- `type`: `MissionType.MISSION`
- `game`: Crée automatiquement un `Game` (SubFactory)
- `creator`: Crée automatiquement un `User` (SubFactory)

**Exemple :**

```python
mission = await MissionFactory.create(title="Mission spéciale", difficulty=75)
```

### RoundFactory

Crée des rounds de test.

**Champs par défaut :**

- `round_number`: `{n + 1}` (séquence)
- `status`: `RoundStatus.RUNNING`
- `lobby`: Crée automatiquement un `Lobby` (SubFactory)

**Exemple :**

```python
round_obj = await RoundFactory.create(round_number=5, status=RoundStatus.FINISHED)
```

### MissionAssignedFactory

Crée des missions assignées de test.

**Champs par défaut :**

- `status`: `MissionAssignedStatus.ACTIVE`
- `player`: Crée automatiquement un `Player` (SubFactory)
- `mission`: Crée automatiquement une `Mission` (SubFactory)

**Exemple :**

```python
mission_assigned = await MissionAssignedFactory.create(
    status=MissionAssignedStatus.COMPLETED
)
```

### TagFactory

Crée des tags de test.

**Champs par défaut :**

- `name`: `"tag-{n}"` (séquence)

**Exemple :**

```python
tag = await TagFactory.create(name="action")
```

## Notes importantes

1. **Session automatique** : Les factories sont automatiquement configurées avec la session de test via `conftest.py`. Vous n'avez pas besoin de les configurer manuellement.

2. **SubFactory** : Les factories utilisent `SubFactory` pour créer automatiquement les objets liés. Cela simplifie la création de scénarios complexes.

3. **Méthode `create()`** : Utilisez `create()` pour créer et sauvegarder des objets en base de données. Les objets sont automatiquement commités et rafraîchis.

4. **Méthode `build()`** : Utilisez `build()` pour créer des objets sans les sauvegarder en base de données. Utile pour tester la validation ou créer des objets temporaires.

5. **Surcharge des relations** : Vous pouvez surcharger les relations créées par `SubFactory` en passant directement les objets :

   ```python
   game = await GameFactory.create()
   user = await UserFactory.create()
   lobby = await LobbyFactory.create(game=game, host=user)
   ```

6. **Séquences** : Les factories utilisent `factory.Sequence` pour générer des valeurs uniques (emails, usernames, etc.).

## Migration depuis l'ancienne approche

Si vous utilisiez l'ancienne approche avec des méthodes `create()` personnalisées :

**Avant :**

```python
user = await UserFactory.create(username="testuser", email="test@example.com")
game = await GameFactory.create(game_type=GameTypeEnum.MISSION)
lobby = await LobbyFactory.create(game_id=game.id, host_id=user.id)
```

**Après :**

```python
user = await UserFactory.create(username="testuser", email="test@example.com")
game = await GameFactory.create(game_type=GameTypeEnum.MISSION)
lobby = await LobbyFactory.create(game=game, host=user)  # Utilise les objets directement
```

La nouvelle approche est plus simple et utilise les relations SQLAlchemy directement.

