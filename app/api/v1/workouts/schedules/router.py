from fastapi import APIRouter, Depends, Query

from app.api.v1.workouts.schema import (
    CreateWorkoutScheduleRequest,
    WorkoutPlanScheduleReadPagination,
)
from app.api.v1.workouts.service import WorkoutPlanService
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_workout_plan_service


router: APIRouter = APIRouter(
    prefix="/{workout_plan_id}/schedules", dependencies=[Depends(validate_jwt)]
)


@router.get("/")
async def get_workout_plan_schedules(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    pagination: WorkoutPlanScheduleReadPagination = Query(...),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    result = await workout_plan_service.get_many_workout_schedules(
        user_id=user_data.id, pagination=pagination, workout_plan_id=workout_plan_id
    )
    return AppResponse(data=result)


@router.get("/{workout_plan_schedule_id}")
async def get_workout_plan_schedule(
    workout_plan_id: int,
    workout_plan_schedule_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    result = await workout_plan_service.get_workout_schedule(
        user_id=user_data.id,
        workout_plan_id=workout_plan_id,
        workout_plan_schedule_id=workout_plan_schedule_id,
    )
    return AppResponse(data=result)


@router.post("/")
async def create_workout_plan_schedule(
    workout_plan_id: int,
    payload: CreateWorkoutScheduleRequest,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    result = await workout_plan_service.create_workout_schedule(
        user_id=user_data.id,
        workout_plan_id=workout_plan_id,
        payload=payload,
    )
    return AppResponse(data=result)
