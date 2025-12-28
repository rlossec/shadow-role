
from app.models import Game, GameTypeEnum

import factory

from .base_factory import BaseFactory


class GameFactory(BaseFactory):
    class Meta:
        model = Game

    name = factory.Sequence(lambda n: f"Game {n}")
    description = "A test game"
    min_players = 2
    max_players = 10
    game_type = GameTypeEnum.MISSION
