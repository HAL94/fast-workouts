from fastapi import APIRouter, Depends
from app.api.v1.schema.workout_plan import ExercisePlanBase
from app.api.v1.workouts.service import WorkoutPlanService


from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse

from app.dependencies.services import get_workout_plan_service
from app.api.v1.workouts.exercise_set_plans.router import router as exercise_set_plans_router


router: APIRouter = APIRouter(
    prefix="/{workout_plan_id}/exercise-plans", dependencies=[Depends(validate_jwt)]
)


@router.get("/")
async def get_exercise_plans(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    workout_exercise_plans = await workout_plan_service.get_workout_exercise_plans(
        workout_plan_id=workout_plan_id, user_id=user_data.id
    )

    return AppResponse(data=workout_exercise_plans)


@router.get("/{exercise_plan_id}")
async def get_exercise_plan(
    workout_plan_id: int,
    exercise_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    workout_exercise_plan = await workout_plan_service.get_workout_exercise_plan(
        workout_plan_id=workout_plan_id,
        exercise_plan_id=exercise_plan_id,
        user_id=user_data.id,
    )

    return AppResponse(data=workout_exercise_plan)


@router.post("/")
async def create_exercise_plan(
    workout_plan_id: int,
    payload: ExercisePlanBase,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    workout_exercise_plan: ExercisePlanBase = await (
        workout_plan_service.create_workout_exercise_plan(
            workout_plan_id=workout_plan_id,
            user_id=user_data.id,
            payload=payload,
        )
    )

    return AppResponse(data=workout_exercise_plan)


@router.patch("/{exercise_plan_id}")
async def update_exercise_plan(
    workout_plan_id: int,
    exercise_plan_id: int,
    payload: ExercisePlanBase,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    workout_exercise_plan: ExercisePlanBase = await (
        workout_plan_service.update_workout_exercise_plan(
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            user_id=user_data.id,
            payload=payload,
        )
    )

    return AppResponse(data=workout_exercise_plan)


@router.delete("/{exercise_plan_id}")
async def delete_exercise_plan(
    workout_plan_id: int,
    exercise_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
):
    result = await workout_plan_service.delete_exercise_plan(
        exercise_plan_id=exercise_plan_id,
        user_id=user_data.id,
        workout_plan_id=workout_plan_id,
    )
    return AppResponse(data=result)

router.include_router(exercise_set_plans_router)