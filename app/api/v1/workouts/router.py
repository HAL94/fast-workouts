from fastapi import APIRouter, Depends, Query

from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest,
    WorkoutPlanReadPagination,
)
from app.api.v1.workouts.service import WorkoutPlanService
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_workout_plan_service
from .exercise_plans.router import router as exercise_plans_router
from .schedules.router import router as workout_schedules_router


router: APIRouter = APIRouter(prefix="/workouts")



@router.get("/")
async def get_workouts(
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
    pagination: WorkoutPlanReadPagination = Query(...),
    user_data: UserRead = Depends(validate_jwt),
):
    data = await workout_plan_service.get_many_workouts(user_data=user_data, pagination=pagination)
    return AppResponse(data=data)


@router.get("/{workout_plan_id}")
async def get_workout_plan(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    data = await workout_plan_service.get_workout_plan(
        workout_plan_id=workout_plan_id, user_data=user_data
    )
    return AppResponse(
        data=data,
        message="Workout plan retrieved successfully",
        success=True,
    )


@router.post("/")
async def create_workout_plan(
    payload: CreateWorkoutPlanRequest,
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
    user_data: UserRead = Depends(validate_jwt),
):
    data = await workout_plan_service.add_workout_plan(
        user_data=user_data, create_data=payload
    )
    return AppResponse(data=data)


@router.patch("/")
async def update_workout_plan(
    payload: UpdateWorkoutPlanRequest,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    data = await workout_plan_service.update_workout_plan(
        data=payload, user_data=user_data
    )
    return AppResponse(data=data)


@router.delete("/{workout_plan_id}")
async def delete_workout_plan(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    data = await workout_plan_service.delete_workout_plan(
        workout_plan_id=workout_plan_id, user_data=user_data
    )
    return AppResponse(data=data)


router.include_router(exercise_plans_router)
router.include_router(workout_schedules_router)