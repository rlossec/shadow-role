
from .authentication import router as auth_router
from .game import router as game_router
from .lobby import router as lobby_router
from .player import router as player_router
from .mission import router as mission_router

__all__ = [
    "auth_router",
    "game_router",
    "lobby_router",
    "player_router",
    "mission_router",
]
