"""
Exemples d'utilisation des factories.

Ce fichier contient des exemples de code montrant comment utiliser les factories.
Ces exemples ne sont pas des tests réels, mais servent de documentation.
"""

from app.models import GameTypeEnum, PlayerStatus, MissionType, RoundStatus, MissionAssignedStatus
from tests.factories import (
    UserFactory,
    GameFactory,
    LobbyFactory,
    PlayerFactory,
    MissionFactory,
    RoundFactory,
    MissionAssignedFactory,
)


# ==================== Exemple 1 : Création simple ====================

async def example_simple_creation(db_session):
    """Exemple de création simple d'objets."""
    # Créer un utilisateur avec les valeurs par défaut
    user = await UserFactory.create()
    
    # Créer un jeu
    game = await GameFactory.create()
    
    # Créer un lobby
    lobby = await LobbyFactory.create(
        game_id=game.id,
        host_id=user.id
    )
    
    return user, game, lobby


# ==================== Exemple 2 : Création avec attributs personnalisés ====================

async def example_custom_attributes(db_session):
    """Exemple de création avec des attributs personnalisés."""
    # Créer un utilisateur avec des attributs spécifiques
    user = await UserFactory.create(
        username="john_doe",
        email="john@example.com",
        is_active=True,
        is_superuser=False
    )
    
    # Créer un jeu avec des paramètres spécifiques
    game = await GameFactory.create(
        name="Mon Super Jeu",
        description="Un jeu fantastique",
        game_type=GameTypeEnum.MISSION,
        min_players=3,
        max_players=6
    )
    
    return user, game


# ==================== Exemple 3 : Scénario complet ====================

async def example_complete_scenario(db_session):
    """Exemple de création d'un scénario complet."""
    # Créer un hôte
    host = await UserFactory.create(username="host")
    
    # Créer un jeu
    game = await GameFactory.create(
        name="Mission Game",
        game_type=GameTypeEnum.MISSION
    )
    
    # Créer des missions
    missions = []
    for i in range(3):
        mission = await MissionFactory.create(
            game_id=game.id,
            title=f"Mission {i+1}",
            description=f"Description de la mission {i+1}",
            difficulty=50 + i * 10,
            mission_type=MissionType.MISSION
        )
        missions.append(mission)
    
    # Créer un lobby
    lobby = await LobbyFactory.create(
        game_id=game.id,
        host_id=host.id,
        name="Mon Lobby",
        min_players=2,
        max_players=6
    )
    
    # Créer des joueurs
    players = []
    for i in range(3):
        user = await UserFactory.create(username=f"player{i}")
        player = await PlayerFactory.create(
            lobby_id=lobby.id,
            user_id=user.id,
            status=PlayerStatus.PLAYING,
            score=i * 10
        )
        players.append(player)
    
    # Créer un round
    round_obj = await RoundFactory.create(
        lobby_id=lobby.id,
        round_number=1,
        status=RoundStatus.RUNNING
    )
    
    # Assigner des missions aux joueurs
    for i, player in enumerate(players):
        await MissionAssignedFactory.create(
            player_id=player.id,
            mission_id=missions[i].id,
            status=MissionAssignedStatus.ACTIVE
        )
    
    return {
        "host": host,
        "game": game,
        "missions": missions,
        "lobby": lobby,
        "players": players,
        "round": round_obj
    }


# ==================== Exemple 4 : Utilisation de build() ====================

async def example_build_method(db_session):
    """Exemple d'utilisation de la méthode build() pour créer des objets non sauvegardés."""
    # Construire un utilisateur sans le sauvegarder
    user = UserFactory.build(
        username="test_user",
        email="test@example.com"
    )
    
    # Construire un jeu sans le sauvegarder
    game = GameFactory.build(
        name="Test Game",
        game_type=GameTypeEnum.MISSION
    )
    
    # Ces objets ne sont pas en base de données
    # Utile pour tester la validation ou créer des objets temporaires
    
    return user, game


# ==================== Exemple 5 : Création en masse ====================

async def example_bulk_creation(db_session):
    """Exemple de création de plusieurs objets."""
    # Créer plusieurs utilisateurs
    users = []
    for i in range(10):
        user = await UserFactory.create(
            username=f"user{i}",
            email=f"user{i}@example.com"
        )
        users.append(user)
    
    # Créer un jeu
    game = await GameFactory.create()
    
    # Créer un lobby
    host = users[0]
    lobby = await LobbyFactory.create(
        game_id=game.id,
        host_id=host.id
    )
    
    # Créer plusieurs joueurs
    players = []
    for user in users[1:6]:  # Utiliser les 5 premiers utilisateurs
        player = await PlayerFactory.create(
            lobby_id=lobby.id,
            user_id=user.id
        )
        players.append(player)
    
    return users, game, lobby, players

