
import factory

from app.models import User

from .base_factory import BaseFactory

class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    hashed_password = "hashed-password"
    is_active = True
    is_superuser = False