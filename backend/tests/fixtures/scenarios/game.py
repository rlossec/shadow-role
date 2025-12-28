"""
Fixtures pour les jeux et missions dans les scénarios de test.

Ce module contient les fixtures pour créer des jeux avec leurs missions associées.
"""

import pytest

from tests.factories import GameFactory, MissionFactory


@pytest.fixture
async def setup_game_with_missions(db_session, count=5):
    """
    Fixture pour créer un jeu avec plusieurs missions.
    
    Args:
        count: Nombre de missions à créer (par défaut: 5)
    
    Returns:
        dict: {
            "game": Game,
            "game_missions": list[Mission]
        }
    """
    game = await GameFactory.create(
        name="Test Game 1",
        min_players=2,
        max_players=10
    )
    
    # Créer `count` missions pour le jeu
    missions = []
    for i in range(count):
        mission = await MissionFactory.create(
            game=game,
            title=f"Mission {i+1}",
            difficulty=50 + i * 10
        )
        missions.append(mission)
    
    return {"game": game, "game_missions": missions}

