"""
Helpers pour les tests API.
"""
from httpx import AsyncClient

from schemas.game_type import GameTypeCreate
from models import User
from schemas import UserCreate
from repositories import GameTypeRepository
from services.auth import AuthenticationService

BASE_GAME_TYPES = [
    {
        "name": "Mission",
        "description": "Des missions secrètes sont assignées aux joueurs, charge aux autres joueurs de les trouver.",
    },
    {
        "name": "Role",
        "description": "Chaque joueur se voit attribuer un rôle. Les autres joueurs doivent découvrir qui est qui.",
    }
]

async def init_game_types(game_type_repository: GameTypeRepository) -> list:
    """
    Initialise les types de jeu de base pour les tests.
    
    Vérifie d'abord si les types existent déjà pour éviter les doublons.
    Retourne la liste des GameType créés ou existants.
    """
    from sqlalchemy import select
    from models import GameType
    
    game_types = []
    for game_type_data in BASE_GAME_TYPES:
        # Vérifier si le type existe déjà
        result = await game_type_repository.db.execute(
            select(GameType).where(GameType.name == game_type_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            game_types.append(existing)
        else:
            game_type = GameTypeCreate(**game_type_data)
            created = await game_type_repository.create_game_type(game_type)
            game_types.append(created)
    
    return game_types

async def create_user_and_get_token(
    client: AsyncClient,
    auth_service: AuthenticationService,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "password123",
) -> tuple[User, str]:
    """Crée un utilisateur actif et retourne l'utilisateur et son token d'accès."""
    user = await auth_service.register_user(
        UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=password,
        )
    )
    user.is_active = True
    await auth_service.user_repository.update_user(user.id, user)
    
    # Obtenir le token
    response = await client.post(
        "/auth/jwt/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return user, token


def get_auth_headers(token: str) -> dict:
    """Retourne les headers d'authentification."""
    return {"Authorization": f"Bearer {token}"}

