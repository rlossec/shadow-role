"""
Service pour gérer les propositions et validations
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from models.player import Player
from models.role import Role
from repositories.role_repository import RoleRepository
from repositories.player_repository import PlayerRepository


class SuggestionService:
    """Service pour gérer les propositions de rôles"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.player_repo = PlayerRepository(db)
    
    # Structure pour stocker les suggestions en mémoire (pourrait être en DB)
    # En production, on pourrait utiliser Redis ou une table dédiée
    _suggestions: Dict[int, Dict] = {}  # {lobby_id: {player_id: {role_id: count}}}
    
    def add_suggestion(
        self, 
        lobby_id: int, 
        player_id: int, 
        target_player_id: int,
        role_id: int
    ) -> bool:
        """
        Enregistre une proposition de rôle pour un joueur.
        
        Args:
            lobby_id: ID du lobby
            player_id: ID du joueur qui fait la proposition
            target_player_id: ID du joueur cible
            role_id: ID du rôle proposé
        
        Returns:
            True si la proposition est valide, False sinon
        """
        if lobby_id not in self._suggestions:
            self._suggestions[lobby_id] = {}
        
        if player_id not in self._suggestions[lobby_id]:
            self._suggestions[lobby_id][player_id] = {}
        
        # Enregistrer la proposition
        key = f"{target_player_id}:{role_id}"
        if key not in self._suggestions[lobby_id][player_id]:
            self._suggestions[lobby_id][player_id][key] = 0
        
        self._suggestions[lobby_id][player_id][key] += 1
        
        return True
    
    def get_suggestions_for_player(
        self, 
        lobby_id: int, 
        target_player_id: int
    ) -> List[Dict]:
        """
        Récupère toutes les propositions pour un joueur donné.
        
        Returns:
            Liste des propositions avec leurs compteurs
        """
        if lobby_id not in self._suggestions:
            return []
        
        suggestions = []
        for proposer_id, props in self._suggestions[lobby_id].items():
            for key, count in props.items():
                target_id, role_id = key.split(":")
                if int(target_id) == target_player_id:
                    suggestions.append({
                        "proposer_id": proposer_id,
                        "target_player_id": int(target_id),
                        "role_id": int(role_id),
                        "count": count
                    })
        
        return suggestions
    
    def get_all_suggestions(self, lobby_id: int) -> Dict:
        """
        Récupère toutes les propositions pour un lobby.
        
        Returns:
            Dictionnaire des propositions par joueur
        """
        return self._suggestions.get(lobby_id, {})
    
    def clear_suggestions(self, lobby_id: int) -> None:
        """Efface toutes les propositions pour un lobby"""
        if lobby_id in self._suggestions:
            del self._suggestions[lobby_id]
    
    def validate_suggestions(
        self, 
        lobby_id: int, 
        player_id: int
    ) -> Optional[int]:
        """
        Valide les propositions et retourne le rôle le plus proposé pour un joueur.
        
        Returns:
            role_id si consensus trouvé, None sinon
        """
        suggestions = self.get_suggestions_for_player(lobby_id, player_id)
        
        if not suggestions:
            return None
        
        # Compter les propositions par rôle
        role_counts: Dict[int, int] = {}
        for suggestion in suggestions:
            role_id = suggestion["role_id"]
            if role_id not in role_counts:
                role_counts[role_id] = 0
            role_counts[role_id] += suggestion["count"]
        
        if not role_counts:
            return None
        
        # Trouver le rôle le plus proposé
        most_suggested_role = max(role_counts.items(), key=lambda x: x[1])
        
        # Peut ajouter une logique de seuil de consensus ici
        # Par exemple: nécessiter au moins 50% des votes
        
        return most_suggested_role[0]
    
    async def check_role_reusability(
        self, 
        role_id: int, 
        lobby_id: int
    ) -> bool:
        """
        Vérifie si un rôle peut être réutilisé dans le lobby.
        Certains rôles peuvent être uniques, d'autres peuvent être réutilisés.
        
        Returns:
            True si le rôle peut être réutilisé, False sinon
        """
        # Récupérer les joueurs du lobby avec leurs rôles
        players = await self.player_repo.get_players_by_lobby(lobby_id)
        
        # Compter combien de fois ce rôle est déjà assigné
        role_count = sum(1 for p in players if p.role_id == role_id)
        
        # Récupérer le rôle pour vérifier ses contraintes
        role = await self.role_repo.get_role(role_id)
        if not role:
            return False
        
        # Si min_players > 0, le rôle peut être réutilisé jusqu'à atteindre min_players
        # Sinon, il est unique (une seule instance)
        if role.min_players == 0:
            return role_count == 0  # Unique si pas déjà assigné
        
        return role_count < role.min_players  # Peut être réutilisé si sous le seuil

