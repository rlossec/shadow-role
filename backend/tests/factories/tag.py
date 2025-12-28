import factory

from app.models import Tag
from .base_factory import BaseFactory


class TagFactory(BaseFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag-{n}")
