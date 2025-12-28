
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.base_factory import BaseFactory


def setup_factories(session: AsyncSession):
    BaseFactory.set_session(session)


def clear_factories():
    BaseFactory.set_session(None)
