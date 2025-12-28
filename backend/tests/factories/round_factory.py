
import factory

from app.models import Round, RoundStatus
from .base_factory import BaseFactory
from .lobby_factory import LobbyFactory


class RoundFactory(BaseFactory):
    class Meta:
        model = Round

    lobby = factory.SubFactory(LobbyFactory)
    round_number = factory.Sequence(lambda n: n + 1)
    status = RoundStatus.RUNNING
