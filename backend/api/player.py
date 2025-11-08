from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.database import get_async_session
from db.schemas import UserResponse, PlayerResponse, PlayerUpdate, PlayerWithUser, PlayerWithRole, RoleResponse, MissionResponse
from repositories.player_repository import PlayerRepository
from repositories.lobby_repository import LobbyRepository
from services.auth import get_current_active_user


router = APIRouter(
    prefix="/api/players",
    tags=["players"]
)


@router.get("/{player_id}", response_model=PlayerWithUser)
async def get_player(
    player_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère les détails d'un joueur"""
    
    player_repository = PlayerRepository(db)
    player = await player_repository.get_player_with_relations(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Créer la réponse avec l'utilisateur
    response = PlayerWithUser.model_validate(player)
    response.user = UserResponse.model_validate(player.user)
    return response


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: UUID,
    player_data: PlayerUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Mettre à jour le statut d'un joueur"""
    player_repository = PlayerRepository(db)
    player = await player_repository.get_player(player_id)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Seul le joueur lui-même ou le host du lobby peut modifier
    lobby_repository = LobbyRepository(db)
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


@router.get("/{player_id}/role", response_model=PlayerWithRole)
async def get_player_role(
    player_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère le rôle assigné à un joueur (secret - vérifie les permissions)"""
    
    player_repository = PlayerRepository(db)
    player = await player_repository.get_player_with_relations(player_id)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Vérifier les permissions : le joueur lui-même ou le host du lobby
    lobby_repository = LobbyRepository(db)
    lobby = await lobby_repository.get_lobby(player.lobby_id)
    
    can_view = (
        player.user_id == current_user.id or
        (lobby and lobby.host_id == current_user.id)
    )
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this player's role"
        )
    
    # Vérifier que le rôle existe
    if not player.role_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No role assigned to this player"
        )
    
    response = PlayerWithRole.model_validate(player)
    if player.role:
        response.role = RoleResponse.model_validate(player.role)
    return response


@router.get("/{player_id}/mission")
async def get_player_missions(
    player_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère les missions assignées à un joueur (secret - vérifie les permissions)"""
    from models.mission_player import MissionPlayer
    
    player_repository = PlayerRepository(db)
    player = await player_repository.get_player(player_id)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Vérifier les permissions : le joueur lui-même ou le host du lobby
    lobby_repository = LobbyRepository(db)
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
    result = await db.execute(
        select(MissionPlayer)
        .options(selectinload(MissionPlayer.mission))
        .where(MissionPlayer.player_id == player_id)
    )
    mission_players = list(result.scalars().all())
    
    # Retourner les missions (pas les MissionPlayer)
    missions = [mp.mission for mp in mission_players if mp.mission]
    return [MissionResponse.model_validate(mission) for mission in missions]


@router.get("/lobby/{lobby_id}", response_model=List[PlayerWithUser])
async def get_lobby_players(
    lobby_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère tous les joueurs d'un lobby"""
    
    # Vérifier que le lobby existe
    lobby_repository = LobbyRepository(db)
    lobby = await lobby_repository.get_lobby(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    # Récupérer les joueurs
    player_repository = PlayerRepository(db)
    players = await player_repository.get_players_by_lobby(lobby_id)
    
    # Construire la réponse avec les utilisateurs
    result = []
    for player in players:
        response = PlayerWithUser.model_validate(player)
        response.user = UserResponse.model_validate(player.user)
        result.append(response)
    
    return result
