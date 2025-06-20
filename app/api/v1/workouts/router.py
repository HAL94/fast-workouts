from fastapi import APIRouter, Depends

from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest,
)
from app.api.v1.workouts.service import WorkoutPlanService
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_workout_plan_service


router: APIRouter = APIRouter(prefix="/workouts")


@router.get("/")
async def get_workouts(
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
    user_data: UserRead = Depends(validate_jwt),
):
    data = await workout_plan_service.get_workouts(user_data=user_data)
    return AppResponse(data=data)


@router.post("/create-workout-plan")
async def create_workout_plan(
    payload: CreateWorkoutPlanRequest,
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
    user_data: UserRead = Depends(validate_jwt),
):
    data = await workout_plan_service.create_workout_plan(
        user_data=user_data, data=payload
    )
    return AppResponse(data=data)


@router.patch("/update-workout-plan")
async def update_workout_plan(
    payload: UpdateWorkoutPlanRequest,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    data = await workout_plan_service.update_workout_plan(
        data=payload, user_data=user_data
    )
    return AppResponse(data=data)


@router.delete("/delete-workout-plan/{workout_plan_id}")
async def delete_workout_plan(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    data = await workout_plan_service.delete_workout_plan(
        workout_plan_id=workout_plan_id, user_data=user_data
    )
    return AppResponse(data=data)
