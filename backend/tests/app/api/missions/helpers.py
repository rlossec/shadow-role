"""
Helpers pour les tests des endpoints missions.

Contient les payloads de base, URLs et fixtures réutilisables.
"""
from uuid import UUID
from typing import Dict, Any

# Import de l'app FastAPI pour le reverse lookup des URLs
from main import app


# Fonctions helper pour générer les URLs via FastAPI reverse lookup
def get_missions_url() -> str:
    """
    Retourne l'URL pour créer une mission via FastAPI reverse lookup.
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("create_mission"))


def get_mission_url(mission_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer une mission via FastAPI reverse lookup.
    
    Args:
        mission_id: UUID de la mission (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_mission", mission_id=str(mission_id)))


def get_create_mission_url() -> str:
    """
    Retourne l'URL pour créer une mission via FastAPI reverse lookup.
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("create_mission"))


def get_update_mission_url(mission_id: UUID | str) -> str:
    """
    Retourne l'URL pour mettre à jour une mission via FastAPI reverse lookup.
    
    Args:
        mission_id: UUID de la mission (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("update_mission", mission_id=str(mission_id)))


def get_delete_mission_url(mission_id: UUID | str) -> str:
    """
    Retourne l'URL pour supprimer une mission via FastAPI reverse lookup.
    
    Args:
        mission_id: UUID de la mission (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("delete_mission", mission_id=str(mission_id)))


def get_missions_by_game_url(game_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer les missions d'un jeu via FastAPI reverse lookup.
    
    Args:
        game_id: UUID du jeu (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_missions_by_game", game_id=str(game_id)))


def get_base_mission_create_payload(game_id: str) -> Dict[str, Any]:
    """
    Retourne un payload de base pour créer une mission.
    
    Les champs obligatoires pour MissionCreate sont: title, description, difficulty, game_id
    
    Args:
        game_id: UUID du jeu (string)
    
    Returns:
        Dict avec les champs obligatoires pour MissionCreate
    """
    return {
        "title": "Test Mission",
        "description": "Test description",
        "difficulty": 50,
        "game_id": game_id
    }


def get_base_mission_update_payload() -> Dict[str, Any]:
    """
    Retourne un payload de base pour mettre à jour une mission.
    
    Tous les champs sont optionnels pour MissionUpdate.
    
    Returns:
        Dict avec quelques champs optionnels pour MissionUpdate
    """
    return {
        "title": "Updated Mission",
        "description": "Updated description",
        "difficulty": 75
    }

