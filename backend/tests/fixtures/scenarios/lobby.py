"""
Fixtures pour les lobbies et joueurs dans les scénarios de test.

Ce module contient les fixtures pour créer des lobbies avec ou sans joueurs.
"""

import pytest
import uuid

from tests.factories import UserFactory, LobbyFactory, PlayerFactory


@pytest.fixture
async def setup_lobby(db_session, setup_game_with_missions):
    """
    Fixture pour créer un lobby avec un hôte.
    
    Args:
        setup_game_with_missions: Fixture qui crée un jeu avec des missions
    
    Returns:
        dict: {
            "lobby": Lobby,
            "game": Game,
            "game_missions": list[Mission],
            "host": User
        }
    """
    game = setup_game_with_missions["game"]
    game_missions = setup_game_with_missions["game_missions"]
    # Utiliser un username unique pour éviter les conflits entre tests
    unique_id = str(uuid.uuid4())[:8]
    host = await UserFactory.create(username=f"host_{unique_id}")
    lobby = await LobbyFactory.create(
        game=game,
        host=host,
        min_players=2,
        max_players=10
    )
    return {"lobby": lobby, "game": game, "game_missions": game_missions, "host": host}


@pytest.fixture
async def setup_lobby_with_players(db_session, setup_lobby, setup_users, count=3):
    """
    Fixture pour créer un lobby avec des joueurs.
    
    Args:
        setup_lobby: Fixture qui crée un lobby
        setup_users: Fixture qui crée des utilisateurs
        count: Nombre de joueurs à créer (par défaut: 3)
    
    Returns:
        dict: {
            "lobby": Lobby,
            "game": Game,
            "game_missions": list[Mission],
            "host": User,
            "users": list[User],
            "players": list[Player]
        }
    """
    lobby = setup_lobby["lobby"]
    game = setup_lobby["game"]
    game_missions = setup_lobby["game_missions"]
    host = setup_lobby["host"]
    users = setup_users
    
    # Créer `count` joueurs
    players = []
    for i in range(count):
        user = users[i]
        player = await PlayerFactory.create(
            lobby=lobby,
            user=user
        )
        players.append(player)

    return {
        "lobby": lobby,
        "game": game,
        "game_missions": game_missions,
        "host": host,
        "users": users,
        "players": players
    }

