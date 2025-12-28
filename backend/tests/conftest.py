"""
Configuration pytest principale pour tous les tests.

Ce fichier configure l'environnement de test et importe les modèles nécessaires.
Toutes les fixtures sont organisées dans tests/fixtures/ et sont chargées via pytest_plugins.
"""
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


from app.models import Game, Lobby, Mission, Player, User, MissionAssigned, Round, Tag

# Charger les modules contenant les fixtures pour qu'elles soient disponibles dans tous les tests
pytest_plugins = [
    "tests.fixtures.scenarios",  # Package de scénarios (users, game, lobby, game_session)
    "tests.fixtures.database",
    "tests.fixtures.authentication",  # Services d'authentification et notifications
    "tests.fixtures.api",
]
