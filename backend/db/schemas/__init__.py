from .user import UserCreate, UserUpdate, UserResponse, UserInDB, UserLogin, UserRead
from .token import (
    AccessToken,
    TokenPair,
    TokenData,
    PasswordResetEmailRequest,
    PasswordResetConfirmRequest,
    AccountActivationRequest,
    AccountActivationConfirmRequest,
    RefreshRequest,
    PasswordResetResponse,
    AccountActivationResponse,
)
from .game import GameCreate, GameResponse, GameUpdate
from .role import RoleCreate, RoleResponse, RoleUpdate
from .mission import MissionCreate, MissionResponse, MissionUpdate
from .player import PlayerCreate, PlayerResponse, PlayerUpdate, PlayerWithUser, PlayerWithRole
from .lobby import LobbyCreate, LobbyResponse, LobbyUpdate, LobbyWithGame


# Résoudre les forward references après tous les imports
LobbyWithGame.model_rebuild()
PlayerWithUser.model_rebuild()
PlayerWithRole.model_rebuild()

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserRead",
    "UserInDB",
    "UserLogin",

    "TokenData",
    "AccessToken",
    "TokenPair",

    "GameCreate",
    "GameResponse",
    "GameUpdate",
    "LobbyCreate",
    "LobbyResponse",
    "LobbyUpdate",
    "LobbyWithGame",
    "RoleCreate",
    "RoleResponse",
    "RoleUpdate",
    "MissionCreate",
    "MissionResponse",
    "MissionUpdate",
    "PlayerCreate",
    "PlayerResponse",
    "PlayerUpdate",
    "PlayerWithUser",
    "PlayerWithRole",
    "PasswordResetEmailRequest",
    "PasswordResetConfirmRequest",
    "AccountActivationRequest",
    "AccountActivationConfirmRequest",
    "RefreshRequest",
    "PasswordResetResponse",
    "AccountActivationResponse",
]
