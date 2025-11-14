from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from schemas import (
    GameResponse,
    GameCreate,
    GameUpdate,
    UserResponse,
    MissionResponse,
)

from repositories.game_repository import GameRepository
from repositories.mission_repository import MissionRepository
from .dependencies import get_game_repository, get_mission_repository, get_current_active_user

router = APIRouter(
    prefix="/api/games",
    tags=["games"]
)


@router.get("", response_model=List[GameResponse], name="list_games")
async def list_games(
    skip: int = 0,
    limit: int = 100,
    game_repository: GameRepository = Depends(get_game_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """List all available game types"""
    games = await game_repository.get_all_games(skip=skip, limit=limit)
    return [GameResponse.model_validate(game) for game in games]


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED, name="create_game")
async def create_game(
    data: GameCreate,
    game_repository: GameRepository = Depends(get_game_repository),
    current_user: UserResponse = Depends(get_current_active_user),
):
    """Create a new game"""
    game = await game_repository.create_game(data)
    return GameResponse.model_validate(game)


@router.get("/{game_id}", response_model=GameResponse, name="get_game")
async def get_game(
    game_id: UUID,
    game_repository: GameRepository = Depends(get_game_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get the details of a game"""
    game = await game_repository.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    # Convertir les tags d'objets Tag en liste de strings
    return GameResponse.model_validate(game)


@router.put("/{game_id}", response_model=GameResponse, name="update_game")
async def update_game(
    game_id: UUID,
    data: GameUpdate,
    game_repository: GameRepository = Depends(get_game_repository),
    current_user: UserResponse = Depends(get_current_active_user),
):
    """Update an existing game"""
    game = await game_repository.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    updated_game = await game_repository.update_game(game, data)
    # Convertir les tags d'objets Tag en liste de strings
    return GameResponse.model_validate(updated_game)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_game")
async def delete_game(
    game_id: UUID,
    game_repository: GameRepository = Depends(get_game_repository),
    current_user: UserResponse = Depends(get_current_active_user),
):
    """Delete a game"""
    game = await game_repository.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    await game_repository.delete_game(game_id)


@router.get("/{game_id}/missions", response_model=List[MissionResponse], name="get_game_missions")
async def get_game_missions(
    game_id: UUID,
    game_repository: GameRepository = Depends(get_game_repository),
    mission_repository: MissionRepository = Depends(get_mission_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get the missions available for a game"""
    game = await game_repository.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get the missions
    missions = await mission_repository.get_missions_by_game(game_id)
    return [MissionResponse.model_validate(mission) for mission in missions]
