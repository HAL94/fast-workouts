from fastapi import APIRouter, Depends, Query

from app.api.v1.muscle_groups.schema import MuscleGroupPagination
from app.api.v1.muscle_groups.service import MuscleGroupService
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_muscle_group_service


router: APIRouter = APIRouter(prefix="/muscle-groups")


@router.get("/")
async def get_muscle_groups(
    pagination: MuscleGroupPagination = Query(...),
    muscle_group_service: MuscleGroupService = Depends(get_muscle_group_service),
):
    result = await muscle_group_service.get_many_muscle_groups(pagination=pagination)

    return AppResponse(data=result)


@router.get("/{muscle_group_id}")
async def get_muscle_group_by_id(
    muscle_group_id: int,
    muscle_group_service: MuscleGroupService = Depends(get_muscle_group_service),
):
    muscle_group = await muscle_group_service.get_muscle_groups_by_id(
        muscle_group_id=muscle_group_id
    )

    return AppResponse(data=muscle_group)


@router.get("/{muscle_group_id}/exercises")
async def get_exercises_by_muscle_group(
    muscle_group_id: int,
    muscle_group_service: MuscleGroupService = Depends(get_muscle_group_service),
):
    exercises = await muscle_group_service.get_exercises_by_muscle_group(
        muscle_group_id
    )
    return AppResponse(data=exercises)
