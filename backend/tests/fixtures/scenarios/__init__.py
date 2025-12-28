"""
Package de scénarios de test.

Ce package contient les fixtures organisées par catégorie pour créer
des scénarios de test réutilisables.
"""

# Imports depuis les modules de scénarios pour les rendre disponibles
# via pytest_plugins dans conftest.py
from tests.fixtures.scenarios.users import (
    setup_users,
    setup_admin_user,
)
from tests.fixtures.scenarios.game import (
    setup_game_with_missions,
)
from tests.fixtures.scenarios.lobby import (
    setup_lobby,
    setup_lobby_with_players,
)
from tests.fixtures.scenarios.game_session import (
    setup_game_session_scenario,
)

__all__ = [
    # Users
    "setup_users",
    "setup_admin_user",
    # Game
    "setup_game_with_missions",
    # Lobby
    "setup_lobby",
    "setup_lobby_with_players",
    # Game Session
    "setup_game_session_scenario",
]

