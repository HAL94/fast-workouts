from fastapi import APIRouter, Depends, Query
from app.api.v1.schema.workout_plan import ExercisePlanBase
from app.api.v1.workouts.schema import ExercisePlanReadPagination
from app.api.v1.workouts.services import ExercisePlanService


from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse

from app.dependencies.services import get_exercise_plan_service
from app.api.v1.workouts.exercise_set_plans.router import router as exercise_set_plans_router


router: APIRouter = APIRouter(
    prefix="/{workout_plan_id}/exercises", dependencies=[Depends(validate_jwt)]
)


@router.get("/")
async def get_exercise_plans(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    pagionation: ExercisePlanReadPagination = Query(...),
    exercise_plan_service: ExercisePlanService = Depends(get_exercise_plan_service),
):
    workout_exercise_plans = await exercise_plan_service.get_many_exercise_plans(
        workout_plan_id=workout_plan_id, user_id=user_data.id, pagionation=pagionation
    )

    return AppResponse(data=workout_exercise_plans)


@router.get("/{exercise_plan_id}")
async def get_exercise_plan(
    workout_plan_id: int,
    exercise_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    exercise_plan_service: ExercisePlanService = Depends(get_exercise_plan_service),
):
    workout_exercise_plan = await exercise_plan_service.get_one_exercise_plan(
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
    exercise_plan_service: ExercisePlanService = Depends(get_exercise_plan_service),
):
    workout_exercise_plan: ExercisePlanBase = await (
        exercise_plan_service.add_exercise_plan_to_workout(
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
    exercise_plan_service: ExercisePlanService = Depends(get_exercise_plan_service),
):
    workout_exercise_plan: ExercisePlanBase = await (
        exercise_plan_service.update_exercise_plan(
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
    exercise_plan_service: ExercisePlanService = Depends(get_exercise_plan_service),
):
    result = await exercise_plan_service.delete_exercise_plan(
        exercise_plan_id=exercise_plan_id,
        user_id=user_data.id,
        workout_plan_id=workout_plan_id,
    )
    return AppResponse(data=result)

router.include_router(exercise_set_plans_router)