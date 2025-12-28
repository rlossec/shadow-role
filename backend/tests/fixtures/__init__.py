"""
Fixtures partagées pour tous les tests.

Ce module contient les scénarios de données réutilisables entre différents types de tests
(services, API, intégration, etc.).
"""

from tests.fixtures.scenarios import (
    setup_game_with_missions,
    setup_lobby_with_players,
)

__all__ = [
    "setup_game_with_missions",
    "setup_lobby_with_players",
]
