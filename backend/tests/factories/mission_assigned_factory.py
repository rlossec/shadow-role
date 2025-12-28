
from app.models import MissionAssigned, MissionAssignedStatus

import factory

from .base_factory import BaseFactory
from .player_factory import PlayerFactory
from .mission_factory import MissionFactory

class MissionAssignedFactory(BaseFactory):
    class Meta:
        model = MissionAssigned

    player = factory.SubFactory(PlayerFactory)
    mission = factory.SubFactory(MissionFactory)
    status = MissionAssignedStatus.ACTIVE
