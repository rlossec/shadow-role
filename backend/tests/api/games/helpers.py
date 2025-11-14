"""
Helpers pour les tests des endpoints games.

Contient les payloads de base, URLs et fixtures réutilisables.
"""
from uuid import UUID
from typing import Dict, Any

# Import de l'app FastAPI pour le reverse lookup des URLs
from main import app


# Fonctions helper pour générer les URLs via FastAPI reverse lookup
def get_games_url() -> str:
    """
    Retourne l'URL pour lister les jeux via FastAPI reverse lookup.
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("list_games"))


def get_game_url(game_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer un jeu via FastAPI reverse lookup.
    
    Args:
        game_id: UUID du jeu (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_game", game_id=str(game_id)))


def get_create_game_url() -> str:
    """
    Retourne l'URL pour créer un jeu via FastAPI reverse lookup.
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("create_game"))


def get_update_game_url(game_id: UUID | str) -> str:
    """
    Retourne l'URL pour mettre à jour un jeu via FastAPI reverse lookup.
    
    Args:
        game_id: UUID du jeu (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("update_game", game_id=str(game_id)))


def get_delete_game_url(game_id: UUID | str) -> str:
    """
    Retourne l'URL pour supprimer un jeu via FastAPI reverse lookup.
    
    Args:
        game_id: UUID du jeu (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("delete_game", game_id=str(game_id)))


def get_game_missions_url(game_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer les missions d'un jeu via FastAPI reverse lookup.
    
    Args:
        game_id: UUID du jeu (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_game_missions", game_id=str(game_id)))


def get_base_game_create_payload(game_type_id: str) -> Dict[str, Any]:
    """
    Retourne un payload de base pour créer un jeu.
    
    Les champs obligatoires pour GameCreate sont: name, description, game_type_id
    
    Args:
        game_type_id: UUID du type de jeu (string)
    
    Returns:
        Dict avec les champs obligatoires pour GameCreate
    """
    return {
        "name": "Test Game",
        "description": "Test description",
        "game_type_id": game_type_id,
        "min_players": 2,
        "max_players": 10
    }


def get_base_game_update_payload() -> Dict[str, Any]:
    """
    Retourne un payload de base pour mettre à jour un jeu.
    
    Tous les champs sont optionnels pour GameUpdate.
    
    Returns:
        Dict avec quelques champs optionnels pour GameUpdate
    """
    return {
        "name": "Updated Game Name",
        "description": "Updated description",
        "min_players": 3,
        "max_players": 12
    }

