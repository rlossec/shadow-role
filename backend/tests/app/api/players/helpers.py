"""
Helpers pour les tests des endpoints players.

Contient les payloads de base, URLs et fixtures réutilisables.
"""
from uuid import UUID
from typing import Dict, Any

# Import de l'app FastAPI pour le reverse lookup des URLs
from main import app


# Fonctions helper pour générer les URLs via FastAPI reverse lookup
def get_player_url(player_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer un joueur via FastAPI reverse lookup.
    
    Args:
        player_id: UUID du joueur (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_player", player_id=str(player_id)))


def get_update_player_url(player_id: UUID | str) -> str:
    """
    Retourne l'URL pour mettre à jour un joueur via FastAPI reverse lookup.
    
    Args:
        player_id: UUID du joueur (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("update_player", player_id=str(player_id)))


def get_player_missions_url(player_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer les missions d'un joueur via FastAPI reverse lookup.
    
    Args:
        player_id: UUID du joueur (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_player_missions", player_id=str(player_id)))


def get_lobby_players_url(lobby_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer les joueurs d'un lobby via FastAPI reverse lookup.
    
    Args:
        lobby_id: UUID du lobby (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_lobby_players", lobby_id=str(lobby_id)))


def get_base_player_update_payload() -> Dict[str, Any]:
    """
    Retourne un payload de base pour mettre à jour un joueur.
    
    Tous les champs sont optionnels pour PlayerUpdate.
    
    Returns:
        Dict avec quelques champs optionnels pour PlayerUpdate
    """
    # Note: PlayerStatus utilise des valeurs en minuscules (waiting, playing, completed, left)
    return {
        "score": 10,
        "status": "waiting"
    }

