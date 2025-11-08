from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.database import get_async_session
from db.schemas import UserResponse, LobbyResponse, LobbyCreate, LobbyWithGame, PlayerResponse

from models import Lobby, LobbyStatus, Player

from services.auth import get_current_active_user
from repositories.lobby_repository import LobbyRepository
from repositories.player_repository import PlayerRepository
from repositories.game_repository import GameRepository


router = APIRouter(
    prefix="/api/lobbies",
    tags=["lobbies"]
)


@router.post("", response_model=LobbyResponse, status_code=status.HTTP_201_CREATED)
async def create_lobby(
    lobby_data: LobbyCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Créer un nouveau lobby"""
    # Vérifier que l'utilisateur n'a pas déjà un lobby actif (en tant que host)
    lobby_repository = LobbyRepository(db)
    existing_lobbies = await db.execute(
        select(Lobby).where(
            and_(
                Lobby.host_id == current_user.id,
                Lobby.status.in_([LobbyStatus.WAITING, LobbyStatus.STARTING, LobbyStatus.IN_PROGRESS])
            )
        )
    )
    if existing_lobbies.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active lobby"
        )
    
    # Vérifier que l'utilisateur n'est pas déjà dans un lobby actif (en tant que joueur)
    player_repository = PlayerRepository(db)
    active_player = await player_repository.get_active_player_by_user(current_user.id)
    if active_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in an active lobby"
        )
    
    # Vérifier que le jeu existe
    game_repository = GameRepository(db)
    game = await game_repository.get_game(lobby_data.game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Créer le lobby
    lobby = await lobby_repository.create_lobby(lobby_data, current_user.id)
    return LobbyResponse.model_validate(lobby)


@router.get("/{lobby_id}", response_model=LobbyWithGame)
async def get_lobby(
    lobby_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère les détails d'un lobby"""
    from db.schemas.game import GameResponse
    
    lobby_repository = LobbyRepository(db)
    lobby = await lobby_repository.get_lobby_with_relations(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    response = LobbyWithGame.model_validate(lobby)
    response.game = GameResponse.model_validate(lobby.game)
    return response


@router.get("", response_model=List[LobbyResponse])
async def list_public_lobbies(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Liste des lobbies publics (en attente)"""
    lobby_repository = LobbyRepository(db)
    lobbies = await lobby_repository.get_public_lobbies(skip=skip, limit=limit)
    return [LobbyResponse.model_validate(lobby) for lobby in lobbies]


@router.post("/{lobby_id}/join", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def join_lobby(
    lobby_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Rejoindre un lobby"""
    from db.schemas.player import PlayerResponse
    
    lobby_repository = LobbyRepository(db)
    player_repository = PlayerRepository(db)
    
    # Vérifier que le lobby existe
    lobby = await lobby_repository.get_lobby(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    # Vérifier que le lobby est en attente
    if lobby.status != LobbyStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lobby is not accepting new players"
        )
    
    # Vérifier que l'utilisateur n'est pas déjà dans un lobby actif
    active_player = await player_repository.get_active_player_by_user(current_user.id)
    if active_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in an active lobby"
        )
    
    # Vérifier qu'il n'est pas déjà dans ce lobby
    existing_player = await db.execute(
        select(Player).where(
            and_(
                Player.lobby_id == lobby_id,
                Player.user_id == current_user.id
            )
        )
    )
    if existing_player.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in this lobby"
        )
    
    # Vérifier le nombre maximum de joueurs
    if lobby.current_players >= lobby.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lobby is full"
        )
    
    # Créer le joueur
    from db.schemas.player import PlayerCreate
    player_data = PlayerCreate(lobby_id=lobby_id)
    player = await player_repository.create_player(player_data, current_user.id)
    
    # Mettre à jour le compteur de joueurs
    await lobby_repository.update_current_players(lobby_id)
    
    return PlayerResponse.model_validate(player)


@router.delete("/{lobby_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lobby(
    lobby_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Supprimer ou quitter un lobby"""
    lobby_repository = LobbyRepository(db)
    player_repository = PlayerRepository(db)
    
    lobby = await lobby_repository.get_lobby(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    # Si c'est le host, supprimer le lobby (et tous les joueurs)
    if lobby.host_id == current_user.id:
        await lobby_repository.delete_lobby(lobby_id)
        return
    
    # Sinon, retirer le joueur du lobby
    player = await db.execute(
        select(Player).where(
            and_(
                Player.lobby_id == lobby_id,
                Player.user_id == current_user.id
            )
        )
    )
    player_obj = player.scalar_one_or_none()
    if not player_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in this lobby"
        )
    
    await player_repository.delete_player(player_obj.id)
    await lobby_repository.update_current_players(lobby_id)


@router.post("/{lobby_id}/start", response_model=LobbyResponse)
async def start_lobby(
    lobby_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Démarrer la partie (seul le host peut le faire)"""
    lobby_repository = LobbyRepository(db)
    
    lobby = await lobby_repository.get_lobby_with_relations(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    # Vérifier que l'utilisateur est le host
    if lobby.host_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can start the lobby"
        )
    
    # Vérifier que le lobby est en attente
    if lobby.status != LobbyStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lobby is not in waiting status"
        )
    
    # Vérifier qu'il y a au moins 2 joueurs
    if lobby.current_players < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lobby needs at least 2 players to start"
        )
    
    # Changer le statut
    lobby.status = LobbyStatus.STARTING
    await db.commit()
    await db.refresh(lobby)
    
    return LobbyResponse.model_validate(lobby)

