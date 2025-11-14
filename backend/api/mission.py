
from uuid import UUID
from typing import List

from fastapi import APIRouter, Response
from fastapi import APIRouter, Depends, HTTPException, status

from repositories import MissionRepository
from schemas import UserResponse, MissionResponse, MissionCreate, MissionUpdate
from .dependencies import get_mission_repository, get_current_active_user


router = APIRouter(
    prefix="/api/missions",
    tags=["missions"]
)


# Créer une mission
@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED, name="create_mission")
async def create_mission(
    mission_data: MissionCreate,
    mission_repository: MissionRepository = Depends(get_mission_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Créer une mission"""
    mission = await mission_repository.create_mission(mission_data)

    return MissionResponse.model_validate(mission)


# Récupérer une mission
@router.get("/{mission_id}", response_model=MissionResponse, name="get_mission")
async def get_mission(
    mission_id: UUID,
    mission_repository: MissionRepository = Depends(get_mission_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    mission = await mission_repository.get_mission(mission_id)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    return MissionResponse.model_validate(mission)


# Mettre à jour une mission
@router.put("/{mission_id}", response_model=MissionResponse, name="update_mission")
async def update_mission(
    mission_id: UUID,
    mission_data: MissionUpdate,
    mission_repository: MissionRepository = Depends(get_mission_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    mission = await mission_repository.update_mission(mission_id, mission_data)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    return MissionResponse.model_validate(mission)


# Supprimer une mission
@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_mission")
async def delete_mission(
    mission_id: UUID,
    mission_repository: MissionRepository = Depends(get_mission_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    mission = await mission_repository.delete_mission(mission_id)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Récupérer les missions d'un jeu
@router.get("/game/{game_id}", response_model=List[MissionResponse], name="get_missions_by_game")
async def get_missions_by_game(
    game_id: UUID,
    mission_repository: MissionRepository = Depends(get_mission_repository),
    current_user: UserResponse = Depends(get_current_active_user)
):
    missions = await mission_repository.get_missions_by_game(game_id)
    return [MissionResponse.model_validate(mission) for mission in missions]