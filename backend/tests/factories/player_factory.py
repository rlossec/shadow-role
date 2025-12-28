
from app.models import Player, PlayerStatus

import factory

from .base_factory import BaseFactory
from .lobby_factory import LobbyFactory
from .user_factory import UserFactory

class PlayerFactory(BaseFactory):
    class Meta:
        model = Player

    lobby = factory.SubFactory(LobbyFactory)
    user = factory.SubFactory(UserFactory)
    status = PlayerStatus.WAITING
    score = 0
