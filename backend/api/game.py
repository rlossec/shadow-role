from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_async_session
from db.schemas import GameResponse, UserResponse, RoleResponse, MissionResponse

from models import Role, Mission

from services.auth import get_current_active_user

from repositories.game_repository import GameRepository


router = APIRouter(
    prefix="/api/games",
    tags=["games"]
)


@router.get("", response_model=List[GameResponse])
async def list_games(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """List all available game types"""
    game_repository = GameRepository(db)
    games = await game_repository.get_all_games(skip=skip, limit=limit)
    return [GameResponse.model_validate(game) for game in games]


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get the details of a game"""
    game_repository = GameRepository(db)
    game = await game_repository.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return GameResponse.model_validate(game)


@router.get("/{game_id}/roles")
async def get_game_roles(
    game_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get the roles available for a game"""
    
    # Verify that the game exists
    game_repository = GameRepository(db)
    game = await game_repository.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get the roles
    result = await db.execute(select(Role).where(Role.game_id == game_id))
    roles = list(result.scalars().all())
    return [RoleResponse.model_validate(role) for role in roles]


@router.get("/{game_id}/missions")
async def get_game_missions(
    game_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get the missions available for a game"""
    
    # Verify that the game exists
    game_repository = GameRepository(db)
    game = await game_repository.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get the missions
    result = await db.execute(select(Mission).where(Mission.game_id == game_id))
    missions = list(result.scalars().all())
    return [MissionResponse.model_validate(mission) for mission in missions]

