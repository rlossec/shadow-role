from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from repositories import LobbyRepository, GameRepository, PlayerRepository

from schemas import (
    UserResponse,
    LobbyResponse,
    LobbyCreate,
)

from .dependencies import get_lobby_repository, get_game_repository, get_player_repository, get_current_active_user


router = APIRouter(
    prefix="/api/lobbies",
    tags=["lobbies"]
)


@router.get("", response_model=List[LobbyResponse])
async def list_public_lobbies(
    skip: int = 0,
    limit: int = 100,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Liste des lobbies publics (en attente)"""
    lobbies = await lobby_repository.get_public_lobbies(skip=skip, limit=limit)
    return [LobbyResponse.model_validate(lobby) for lobby in lobbies]


@router.post("", response_model=LobbyResponse, status_code=status.HTTP_201_CREATED)
async def create_lobby(
    lobby_data: LobbyCreate,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    game_repository: GameRepository = Depends(get_game_repository),
    player_repository: PlayerRepository = Depends(get_player_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Créer un nouveau lobby"""
    # Vérifier que l'utilisateur n'a pas déjà un lobby actif (en tant que host)
    existing_lobbies = await lobby_repository.get_user_active_lobbies(current_user.id)
    if existing_lobbies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active lobby"
        )
    
    # Vérifier que l'utilisateur n'est pas déjà dans un lobby actif (en tant que joueur)
    active_player = await player_repository.get_active_player_by_user(current_user.id)
    if active_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in an active lobby"
        )
    
    # Vérifier que le jeu existe
    game = await game_repository.get_game(lobby_data.game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Créer le lobby
    lobby = await lobby_repository.create_lobby(lobby_data, current_user.id)
    return LobbyResponse.model_validate(lobby)


@router.get("/{lobby_id}", response_model=LobbyResponse)
async def get_lobby(
    lobby_id: UUID,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère les détails d'un lobby avec le jeu associé"""

    lobby = await lobby_repository.get_lobby_with_relations(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    return LobbyResponse.model_validate(lobby)


@router.get("/code/{code}", response_model=LobbyResponse)
async def get_lobby_by_code(
    code: str,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user),
):
    """Récupère un lobby via son code unique avec le jeu associé."""
    lobby = await lobby_repository.get_lobby_with_relations_by_code(code)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )

    return LobbyResponse.model_validate(lobby)


@router.delete("/{lobby_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lobby(
    lobby_id: UUID,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Supprimer un lobby (seul le host peut le faire)"""
    lobby = await lobby_repository.get_lobby(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    # Si c'est le host, supprimer le lobby (et tous les joueurs)
    if lobby.host_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the host of this lobby"
        )

    await lobby_repository.delete_lobby(lobby_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
