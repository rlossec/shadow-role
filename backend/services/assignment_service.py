"""
Service pour l'attribution aléatoire des rôles et missions
"""
import random
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from models.player import Player
from models.role import Role
from models.mission import Mission
from models.game import GameType
from repositories.role_repository import RoleRepository
from repositories.mission_repository import MissionRepository
from repositories.player_repository import PlayerRepository


class AssignmentService:
    """Service pour gérer l'attribution aléatoire des rôles et missions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.mission_repo = MissionRepository(db)
        self.player_repo = PlayerRepository(db)
    
    async def assign_roles_to_players(
        self, 
        players: List[Player], 
        game_id: int
    ) -> Dict[int, int]:
        """
        Attribue aléatoirement des rôles aux joueurs.
        Respecte les contraintes min_players pour chaque rôle.
        
        Returns:
            Dict[player_id, role_id]
        """
        # Récupérer tous les rôles disponibles pour ce jeu
        roles = await self.role_repo.get_roles_with_relations(game_id)
        
        if not roles:
            return {}
        
        # Préparer la distribution des rôles
        role_assignments: Dict[int, int] = {}
        available_roles: List[Role] = []
        
        # D'abord, satisfaire les min_players pour chaque rôle
        for role in roles:
            if role.min_players > 0:
                # Ajouter ce rôle min_players fois
                for _ in range(role.min_players):
                    available_roles.append(role)
        
        # Ensuite, remplir avec les rôles restants aléatoirement
        remaining_players = len(players) - len(available_roles)
        if remaining_players > 0:
            for _ in range(remaining_players):
                available_roles.append(random.choice(roles))
        
        # Mélanger aléatoirement
        random.shuffle(available_roles)
        
        # Attribuer les rôles aux joueurs
        for i, player in enumerate(players):
            if i < len(available_roles):
                role_assignments[player.id] = available_roles[i].id
            else:
                # Si pas assez de rôles, attribuer un rôle aléatoire
                role_assignments[player.id] = random.choice(roles).id
        
        return role_assignments
    
    async def assign_missions_to_players(
        self,
        players: List[Player],
        game_id: int,
        game_type: GameType
    ) -> Dict[int, Dict]:
        """
        Attribue des missions aux joueurs selon le type de jeu.
        
        Returns:
            Dict[player_id, Dict avec les missions assignées]
        """
        missions_by_player: Dict[int, Dict] = {}
        
        # Récupérer toutes les missions du jeu
        all_missions = await self.mission_repo.get_missions_by_game(game_id)
        
        if not all_missions:
            return missions_by_player
        
        if game_type == GameType.MISSION_BASED:
            # Mode mission-based: chaque joueur reçoit une ou plusieurs missions
            for player in players:
                # Choisir une mission aléatoire non assignée
                available_missions = await self.mission_repo.get_available_missions(
                    game_id, player.id
                )
                if available_missions:
                    selected_mission = random.choice(available_missions)
                    mission_player = await self.mission_repo.assign_mission_to_player(
                        player.id, selected_mission.id
                    )
                    missions_by_player[player.id] = {
                        "mission": selected_mission,
                        "mission_player": mission_player
                    }
        
        elif game_type == GameType.ROLE_BASED:
            # Mode role-based: missions liées au rôle du joueur
            for player in players:
                if player.role_id:
                    # Missions liées au rôle
                    role_missions = await self.mission_repo.get_missions_by_role(
                        player.role_id
                    )
                    if role_missions:
                        selected_mission = random.choice(role_missions)
                        mission_player = await self.mission_repo.assign_mission_to_player(
                            player.id, selected_mission.id
                        )
                        missions_by_player[player.id] = {
                            "mission": selected_mission,
                            "mission_player": mission_player
                        }
        
        elif game_type == GameType.HYBRID:
            # Mode hybride: combinaison des deux
            for player in players:
                # Priorité aux missions liées au rôle, sinon mission générale
                if player.role_id:
                    role_missions = await self.mission_repo.get_missions_by_role(
                        player.role_id
                    )
                    if role_missions:
                        selected_mission = random.choice(role_missions)
                    else:
                        available_missions = await self.mission_repo.get_available_missions(
                            game_id, player.id
                        )
                        if available_missions:
                            selected_mission = random.choice(available_missions)
                        else:
                            continue
                else:
                    available_missions = await self.mission_repo.get_available_missions(
                        game_id, player.id
                    )
                    if available_missions:
                        selected_mission = random.choice(available_missions)
                    else:
                        continue
                
                mission_player = await self.mission_repo.assign_mission_to_player(
                    player.id, selected_mission.id
                )
                missions_by_player[player.id] = {
                    "mission": selected_mission,
                    "mission_player": mission_player
                }
        
        return missions_by_player
    
    async def apply_role_assignments(
        self, 
        role_assignments: Dict[int, int]
    ) -> None:
        """Applique les attributions de rôles aux joueurs en base de données"""
        for player_id, role_id in role_assignments.items():
            from schemas.player import PlayerUpdate
            update_data = PlayerUpdate(role_id=role_id)
            await self.player_repo.update_player(player_id, update_data)

