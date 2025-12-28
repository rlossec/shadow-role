import factory
from app.models import Lobby, LobbyStatus, LobbyPhase

from .base_factory import BaseFactory
from .game_factory import GameFactory
from .user_factory import UserFactory


class LobbyFactory(BaseFactory):
    class Meta:
        model = Lobby

    name = factory.Sequence(lambda n: f"Lobby {n}")
    code = factory.Sequence(lambda n: f"CODE{n}")
    status = LobbyStatus.WAITING
    phase = LobbyPhase.NONE

    game = factory.SubFactory(GameFactory)
    host = factory.SubFactory(UserFactory)