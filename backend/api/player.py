from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from schemas import UserResponse, PlayerResponse, PlayerUpdate, MissionResponse
from repositories.player_repository import PlayerRepository
from repositories.lobby_repository import LobbyRepository
from .dependencies import get_player_repository, get_lobby_repository, get_current_active_user


router = APIRouter(
    prefix="/api/players",
    tags=["players"]
)


@router.get("/{player_id}", response_model=PlayerResponse, name="get_player")
async def get_player(
    player_id: UUID,
    player_repository: PlayerRepository = Depends(get_player_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère les détails d'un joueur"""
    player = await player_repository.get_player_with_relations(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    # Créer la réponse avec l'utilisateur
    response = PlayerResponse.model_validate(player)
    return response


@router.put("/{player_id}", response_model=PlayerResponse, name="update_player")
async def update_player(
    player_id: UUID,
    player_data: PlayerUpdate,
    player_repository: PlayerRepository = Depends(get_player_repository),
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Mettre à jour le statut d'un joueur"""
    player = await player_repository.get_player(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    # Seul le joueur lui-même ou le host du lobby peut modifier
    lobby = await lobby_repository.get_lobby(player.lobby_id)
    
    can_modify = (
        player.user_id == current_user.id or
        (lobby and lobby.host_id == current_user.id)
    )
    
    if not can_modify:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this player"
        )
    
    updated_player = await player_repository.update_player(player_id, player_data)
    return PlayerResponse.model_validate(updated_player)


@router.get("/{player_id}/mission", name="get_player_missions")
async def get_player_missions(
    player_id: UUID,
    player_repository: PlayerRepository = Depends(get_player_repository),
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère les missions assignées à un joueur (secret - vérifie les permissions)"""
    player = await player_repository.get_player(player_id)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Vérifier les permissions : le joueur lui-même ou le host du lobby
    lobby = await lobby_repository.get_lobby(player.lobby_id)
    
    can_view = (
        player.user_id == current_user.id or
        (lobby and lobby.host_id == current_user.id)
    )
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this player's missions"
        )
    
    # Récupérer les missions du joueur  
    player_missions = await player_repository.get_player_missions(player_id)
    
    # Retourner les missions (pas les MissionAssigned)
    missions = [mission for mission in player_missions]
    return [MissionResponse.model_validate(mission) for mission in missions]


@router.get("/lobby/{lobby_id}", response_model=List[PlayerResponse], name="get_lobby_players")
async def get_lobby_players(
    lobby_id: UUID,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    player_repository: PlayerRepository = Depends(get_player_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère tous les joueurs d'un lobby"""
    
    # Vérifier que le lobby existe
    lobby = await lobby_repository.get_lobby(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    # Récupérer les joueurs
    players = await player_repository.get_players_by_lobby(lobby_id)
    
    return [PlayerResponse.model_validate(player) for player in players]
