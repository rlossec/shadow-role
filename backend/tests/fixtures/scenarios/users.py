"""
Fixtures pour les utilisateurs dans les scénarios de test.

Ce module contient les fixtures pour créer des comptes utilisateurs
de différents types (utilisateurs standards, administrateurs, etc.).
"""

import pytest

from tests.factories import UserFactory


@pytest.fixture
async def setup_users(db_session, count=5):
    """
    Fixture pour créer des comptes utilisateurs.
    
    Args:
        count: Nombre d'utilisateurs à créer (par défaut: 5)
    
    Returns:
        list[User]: Liste des utilisateurs créés
    """
    users = []
    for i in range(count):
        user = await UserFactory.create(username=f"user{i+1}")
        users.append(user)
    return users


@pytest.fixture
async def setup_admin_user(db_session):
    """
    Fixture pour créer un compte utilisateur administrateur.
    
    Returns:
        User: Utilisateur administrateur créé
    """
    admin_user = await UserFactory.create(username="admin", is_superuser=True)
    return admin_user

