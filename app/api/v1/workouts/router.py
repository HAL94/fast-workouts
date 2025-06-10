from fastapi import APIRouter, Depends

from app.api.v1.workouts.schema import CreateWorkoutPlanRequest
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
