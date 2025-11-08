"""
Service pour gérer les transitions de phases du jeu
"""
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from models.lobby import Lobby, LobbyStatus
from models.player import Player, PlayerStatus
from models.game import GameType
from repositories.lobby_repository import LobbyRepository
from repositories.player_repository import PlayerRepository
from repositories.game_repository import GameRepository
from services.assignment_service import AssignmentService
from services.suggestion_service import SuggestionService


class GamePhase:
    """Phases du jeu"""
    WAITING = "waiting"  # Attente des joueurs
    SUGGESTION = "suggestion"  # Phase de suggestion de rôles
    ASSIGNMENT = "assignment"  # Phase d'attribution des rôles
    PLAYING = "playing"  # Phase de jeu
    VALIDATION = "validation"  # Phase de validation
    FINISHED = "finished"  # Partie terminée


class GameService:
    """Service pour gérer les transitions de phases du jeu"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lobby_repo = LobbyRepository(db)
        self.player_repo = PlayerRepository(db)
        self.game_repo = GameRepository(db)
        self.assignment_service = AssignmentService(db)
        self.suggestion_service = SuggestionService(db)
        
        # État en mémoire pour chaque lobby (phase actuelle, etc.)
        # En production, on pourrait stocker ça en DB ou Redis
        self._game_states: Dict[int, Dict] = {}  # {lobby_id: {phase, round_number, ...}}
    
    def get_game_state(self, lobby_id: int) -> Dict:
        """Récupère l'état du jeu pour un lobby"""
        return self._game_states.get(lobby_id, {
            "phase": GamePhase.WAITING,
            "round_number": 0,
            "round_type": None
        })
    
    def set_game_state(self, lobby_id: int, state: Dict) -> None:
        """Met à jour l'état du jeu pour un lobby"""
        self._game_states[lobby_id] = state
    
    async def start_game(
        self, 
        lobby_id: int, 
        game_type: Optional[GameType] = None
    ) -> Dict:
        """
        Lance une partie.
        
        Transition: WAITING -> SUGGESTION ou ASSIGNMENT
        """
        lobby = await self.lobby_repo.get_lobby_with_relations(lobby_id)
        if not lobby:
            raise ValueError("Lobby not found")
        
        if lobby.status != LobbyStatus.WAITING:
            raise ValueError(f"Lobby is not in WAITING status: {lobby.status}")
        
        players = await self.player_repo.get_players_by_lobby(lobby_id)
        if len(players) < 2:
            raise ValueError("Not enough players to start the game")
        
        # Déterminer le type de jeu si non fourni
        if game_type is None:
            if lobby.game:
                game_type = lobby.game.type
            else:
                game_type = GameType.HYBRID
        
        # Mettre à jour le statut du lobby
        from schemas.lobby import LobbyUpdate
        lobby_update = LobbyUpdate(status=LobbyStatus.STARTING)
        await self.lobby_repo.update_lobby(lobby_id, lobby_update)
        
        # Initialiser l'état du jeu
        self.set_game_state(lobby_id, {
            "phase": GamePhase.SUGGESTION,
            "round_number": 1,
            "game_type": game_type.value if isinstance(game_type, GameType) else game_type
        })
        
        # Mettre à jour les statuts des joueurs
        for player in players:
            from schemas.player import PlayerUpdate
            player_update = PlayerUpdate(status=PlayerStatus.PLAYING)
            await self.player_repo.update_player(player.id, player_update)
        
        # Finaliser le statut du lobby
        lobby_update = LobbyUpdate(status=LobbyStatus.IN_PROGRESS)
        await self.lobby_repo.update_lobby(lobby_id, lobby_update)
        
        return {
            "lobby_id": lobby_id,
            "phase": GamePhase.SUGGESTION,
            "players": [self._player_to_dict(p) for p in players],
            "game_type": game_type.value if isinstance(game_type, GameType) else game_type
        }
    
    async def start_round(
        self, 
        lobby_id: int, 
        round_type: Optional[str] = None
    ) -> Dict:
        """
        Lance une nouvelle manche.
        
        Transition: VALIDATION -> SUGGESTION ou ASSIGNMENT -> PLAYING
        """
        state = self.get_game_state(lobby_id)
        
        if state["phase"] not in [GamePhase.VALIDATION, GamePhase.ASSIGNMENT]:
            raise ValueError(f"Cannot start round from phase: {state['phase']}")
        
        # Incrémenter le numéro de manche
        state["round_number"] = state.get("round_number", 0) + 1
        state["round_type"] = round_type
        state["phase"] = GamePhase.PLAYING
        
        self.set_game_state(lobby_id, state)
        
        return {
            "lobby_id": lobby_id,
            "phase": GamePhase.PLAYING,
            "round_number": state["round_number"],
            "round_type": round_type
        }
    
    async def transition_to_assignment(self, lobby_id: int) -> Dict:
        """
        Transition de SUGGESTION vers ASSIGNMENT.
        Attribue les rôles basés sur les suggestions validées.
        """
        state = self.get_game_state(lobby_id)
        
        if state["phase"] != GamePhase.SUGGESTION:
            raise ValueError(f"Cannot transition to assignment from phase: {state['phase']}")
        
        players = await self.player_repo.get_players_by_lobby(lobby_id)
        lobby = await self.lobby_repo.get_lobby_with_relations(lobby_id)
        
        if not lobby or not lobby.game:
            raise ValueError("Lobby or game not found")
        
        game_type = GameType(state.get("game_type", GameType.HYBRID.value))
        
        # Phase d'attribution: assigner les rôles
        role_assignments = await self.assignment_service.assign_roles_to_players(
            players, 
            lobby.game_id
        )
        
        # Appliquer les attributions
        await self.assignment_service.apply_role_assignments(role_assignments)
        
        # Attribuer les missions si nécessaire
        missions_by_player = await self.assignment_service.assign_missions_to_players(
            players,
            lobby.game_id,
            game_type
        )
        
        # Rafraîchir les joueurs pour avoir les rôles à jour
        players = await self.player_repo.get_players_by_lobby(lobby_id)
        
        state["phase"] = GamePhase.ASSIGNMENT
        self.set_game_state(lobby_id, state)
        
        return {
            "lobby_id": lobby_id,
            "phase": GamePhase.ASSIGNMENT,
            "role_assignments": role_assignments,
            "missions_by_player": {
                pid: {
                    "mission_id": m["mission"].id,
                    "mission": {
                        "id": m["mission"].id,
                        "title": m["mission"].title,
                        "description": m["mission"].description,
                        "is_known_by_player": m["mission"].is_known_by_player,
                        "is_known_by_others": m["mission"].is_known_by_others
                    }
                }
                for pid, m in missions_by_player.items()
            }
        }
    
    async def transition_to_validation(self, lobby_id: int) -> Dict:
        """
        Transition de PLAYING vers VALIDATION.
        Phase de validation des résultats.
        """
        state = self.get_game_state(lobby_id)
        
        if state["phase"] != GamePhase.PLAYING:
            raise ValueError(f"Cannot transition to validation from phase: {state['phase']}")
        
        state["phase"] = GamePhase.VALIDATION
        self.set_game_state(lobby_id, state)
        
        # Calculer les scores si nécessaire
        players = await self.player_repo.get_players_by_lobby(lobby_id)
        
        return {
            "lobby_id": lobby_id,
            "phase": GamePhase.VALIDATION,
            "players": [self._player_to_dict(p) for p in players]
        }
    
    async def end_game(self, lobby_id: int) -> Dict:
        """
        Termine la partie.
        
        Transition: VALIDATION ou PLAYING -> FINISHED
        """
        state = self.get_game_state(lobby_id)
        
        # Mettre à jour le statut du lobby
        from schemas.lobby import LobbyUpdate
        lobby_update = LobbyUpdate(status=LobbyStatus.FINISHED)
        await self.lobby_repo.update_lobby(lobby_id, lobby_update)
        
        # Mettre à jour les statuts des joueurs
        players = await self.player_repo.get_players_by_lobby(lobby_id)
        for player in players:
            from schemas.player import PlayerUpdate
            player_update = PlayerUpdate(status=PlayerStatus.COMPLETED)
            await self.player_repo.update_player(player.id, player_update)
        
        state["phase"] = GamePhase.FINISHED
        self.set_game_state(lobby_id, state)
        
        # Nettoyer les suggestions
        self.suggestion_service.clear_suggestions(lobby_id)
        
        return {
            "lobby_id": lobby_id,
            "phase": GamePhase.FINISHED,
            "players": [self._player_to_dict(p) for p in players]
        }
    
    def _player_to_dict(self, player: Player) -> Dict:
        """Convertit un joueur en dictionnaire pour la sérialisation"""
        result = {
            "id": player.id,
            "user_id": player.user_id,
            "lobby_id": player.lobby_id,
            "score": player.score,
            "status": player.status.value if hasattr(player.status, 'value') else str(player.status)
        }
        
        if player.user:
            result["username"] = player.user.username
        
        if player.role:
            result["role"] = {
                "id": player.role.id,
                "name": player.role.name,
                "description": player.role.description,
                "image_url": player.role.image_url
            }
        
        return result

