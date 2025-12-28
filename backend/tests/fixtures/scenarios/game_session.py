"""
Fixtures pour les scénarios complets de session de jeu.

Ce module contient les fixtures pour créer des scénarios complets et complexes
utilisés pour tester les handlers et services de jeu.
"""

import pytest

from tests.factories import (
    UserFactory,
    GameFactory,
    LobbyFactory,
    MissionFactory,
    PlayerFactory,
)


@pytest.fixture
async def setup_game_session_scenario(db_session):
    """
    Fixture pour créer un scénario complet pour tester les handlers et services.
    
    Crée :
    - Un jeu avec des missions
    - Un lobby avec un hôte
    - Des joueurs dans le lobby
    
    Returns:
        dict: {
            "host": User,
            "game": Game,
            "missions": list[Mission],
            "lobby": Lobby,
            "players": list[Player],
            "users": list[User]
        }
    """
    # Créer un hôte
    host = await UserFactory.create(username="host", email="host@test.com")
    
    # Créer un jeu avec des missions
    game = await GameFactory.create(name="Test Game")
    
    # Créer 5 missions pour le jeu
    missions = []
    for i in range(5):
        mission = await MissionFactory.create(
            game=game,
            title=f"Mission {i+1}",
            creator=host
        )
        missions.append(mission)
    
    # Créer un lobby
    lobby = await LobbyFactory.create(game=game, host=host, min_players=2)
    
    # Créer des joueurs
    user1 = await UserFactory.create(username="user1", email="user1@test.com")
    user2 = await UserFactory.create(username="user2", email="user2@test.com")
    player1 = await PlayerFactory.create(lobby=lobby, user=user1)
    player2 = await PlayerFactory.create(lobby=lobby, user=user2)
    
    return {
        "host": host,
        "game": game,
        "missions": missions,
        "lobby": lobby,
        "players": [player1, player2],
        "users": [user1, user2]
    }

