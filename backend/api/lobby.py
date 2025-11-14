from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from repositories import LobbyRepository, GameRepository, PlayerRepository

from schemas import (
    LobbyUpdate,
    UserResponse,
    LobbyResponse,
    LobbyCreate,
)

from .dependencies import get_lobby_repository, get_game_repository, get_player_repository, get_current_active_user


router = APIRouter(
    prefix="/api/lobbies",
    tags=["lobbies"]
)


@router.get("", response_model=List[LobbyResponse], name="list_lobbies")
async def list_lobbies(
    skip: int = 0,
    limit: int = 100,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """List all lobbies"""
    lobbies = await lobby_repository.get_lobbies(skip=skip, limit=limit)
    return [LobbyResponse.model_validate(lobby) for lobby in lobbies]


@router.post("", response_model=LobbyResponse, status_code=status.HTTP_201_CREATED, name="create_lobby")
async def create_lobby(
    lobby_data: LobbyCreate,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    game_repository: GameRepository = Depends(get_game_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Créer un nouveau lobby"""
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


@router.get("/{lobby_id}", response_model=LobbyResponse, name="get_lobby")
async def get_lobby(
    lobby_id: UUID,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Récupère les détails d'un lobby avec le jeu associé"""

    lobby = await lobby_repository.get_lobby_with_game_and_players(lobby_id)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found"
        )
    
    return LobbyResponse.model_validate(lobby)


@router.put("/{lobby_id}", response_model=LobbyResponse, name="update_lobby")
async def update_lobby(
    lobby_id: UUID,
    lobby_data: LobbyUpdate,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Mettre à jour un lobby"""
    lobby = await lobby_repository.get_lobby(lobby_id)
    if not lobby or lobby.host_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the host of this lobby"
        )
    
    updated_lobby = await lobby_repository.update_lobby(lobby_id, lobby_data)
    return LobbyResponse.model_validate(updated_lobby)


@router.delete("/{lobby_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_lobby")
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


@router.get("/code/{code}", response_model=LobbyResponse, name="get_lobby_by_code")
async def get_lobby_by_code(
    code: str,
    lobby_repository: LobbyRepository = Depends(get_lobby_repository),
    current_user: UserResponse = Depends(get_current_active_user),
):
    """Récupère un lobby via son code unique avec le jeu associé."""
    lobby = await lobby_repository.get_lobby_with_game_and_players_by_code(code)
    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )

    return LobbyResponse.model_validate(lobby)