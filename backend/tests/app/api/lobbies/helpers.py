"""
Helpers pour les tests des endpoints lobbies.

Contient les payloads de base, URLs et fixtures réutilisables.
"""
from uuid import UUID
from typing import Dict, Any

# Import de l'app FastAPI pour le reverse lookup des URLs
from main import app


# Fonctions helper pour générer les URLs via FastAPI reverse lookup
def get_lobbies_url() -> str:
    """
    Retourne l'URL pour lister/créer les lobbies via FastAPI reverse lookup.
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("list_lobbies"))


def get_lobby_url(lobby_id: UUID | str) -> str:
    """
    Retourne l'URL pour récupérer/mettre à jour/supprimer un lobby via FastAPI reverse lookup.
    
    Args:
        lobby_id: UUID du lobby (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_lobby", lobby_id=str(lobby_id)))


def get_lobby_by_code_url(code: str) -> str:
    """
    Retourne l'URL pour récupérer un lobby par code via FastAPI reverse lookup.
    
    Args:
        code: Code du lobby
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("get_lobby_by_code", code=code))


def get_create_lobby_url() -> str:
    """
    Retourne l'URL pour créer un lobby via FastAPI reverse lookup.
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("create_lobby"))


def get_update_lobby_url(lobby_id: UUID | str) -> str:
    """
    Retourne l'URL pour mettre à jour un lobby via FastAPI reverse lookup.
    
    Args:
        lobby_id: UUID du lobby (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("update_lobby", lobby_id=str(lobby_id)))


def get_delete_lobby_url(lobby_id: UUID | str) -> str:
    """
    Retourne l'URL pour supprimer un lobby via FastAPI reverse lookup.
    
    Args:
        lobby_id: UUID du lobby (UUID ou string)
    
    Returns:
        URL générée depuis le nom de la route FastAPI
    """
    return str(app.url_path_for("delete_lobby", lobby_id=str(lobby_id)))


def get_base_lobby_create_payload(game_id: str) -> Dict[str, Any]:
    """
    Retourne un payload de base pour créer un lobby.
    
    Args:
        game_id: UUID du jeu (string)
    
    Returns:
        Dict avec les champs obligatoires pour LobbyCreate
    """
    return {
        "name": "Test Lobby",
        "game_id": game_id,
        "min_players": 2,
        "max_players": 10
    }


def get_base_lobby_update_payload(game_id: str = None) -> Dict[str, Any]:
    """
    Retourne un payload de base pour mettre à jour un lobby.
    
    Tous les champs sont optionnels pour LobbyUpdate.
    
    Args:
        game_id: UUID du jeu (string, optionnel)
    
    Returns:
        Dict avec quelques champs optionnels pour LobbyUpdate
    """
    payload = {
        "name": "Updated Lobby Name",
        "min_players": 3,
        "max_players": 12
    }
    if game_id is not None:
        payload["game_id"] = game_id
    return payload

