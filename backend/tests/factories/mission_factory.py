
from app.models import Mission, MissionType

import factory

from .base_factory import BaseFactory
from .game_factory import GameFactory
from .user_factory import UserFactory


class MissionFactory(BaseFactory):
    class Meta:
        model = Mission

    title = factory.Sequence(lambda n: f"Mission {n}")
    description = "Do something"
    difficulty = 50
    type = MissionType.MISSION

    game = factory.SubFactory(GameFactory)
    creator = factory.SubFactory(UserFactory)
