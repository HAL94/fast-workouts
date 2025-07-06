from fastapi import APIRouter, Depends, Query

from app.api.v1.schema.workout_plan import ExerciseSetPlanBase
from app.api.v1.workouts.schema import ExerciseSetPlanReadPagination
from app.api.v1.workouts.services import ExerciseSetPlanService
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_exercise_set_plan_service

router: APIRouter = APIRouter(
    prefix="/{exercise_plan_id}/sets",
    dependencies=[Depends(validate_jwt)],
)


@router.get("/{exercise_set_plan_id}")
async def get_exercise_set_plan(
    workout_plan_id: int,
    exercise_plan_id: int,
    exercise_set_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetPlanService = Depends(
        get_exercise_set_plan_service
    ),
):
    result = await exercise_set_service.get_one_set_plan(
        workout_plan_id=workout_plan_id,
        exercise_plan_id=exercise_plan_id,
        exercise_set_plan_id=exercise_set_plan_id,
        user_id=user_data.id,
    )

    return AppResponse(data=result)


@router.get("/")
async def get_exercise_set_plans(
    workout_plan_id: int,
    exercise_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    pagination: ExerciseSetPlanReadPagination = Query(...),
    exercise_set_service: ExerciseSetPlanService = Depends(
        get_exercise_set_plan_service
    ),
):
    result = await exercise_set_service.get_many_set_plans(
        workout_plan_id=workout_plan_id,
        exercise_plan_id=exercise_plan_id,
        user_id=user_data.id,
        pagination=pagination,
    )

    return AppResponse(data=result)


@router.post("/")
async def create_exercise_set_plan(
    workout_plan_id: int,
    exercise_plan_id: int,
    payload: ExerciseSetPlanBase,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetPlanService = Depends(
        get_exercise_set_plan_service
    ),
):
    result = await exercise_set_service.add_set_to_exercise_plan(
        exercise_plan_id=exercise_plan_id,
        workout_plan_id=workout_plan_id,
        user_id=user_data.id,
        payload=payload,
    )

    return AppResponse(data=result)


@router.patch("/{exercise_set_plan_id}")
async def update_exercise_set_plan(
    workout_plan_id: int,
    exercise_plan_id: int,
    exercise_set_plan_id: int,
    payload: ExerciseSetPlanBase,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetPlanService = Depends(
        get_exercise_set_plan_service
    ),
):
    result = await exercise_set_service.update_set_plan(
        exercise_set_plan_id=exercise_set_plan_id,
        exercise_plan_id=exercise_plan_id,
        workout_plan_id=workout_plan_id,
        user_id=user_data.id,
        payload=payload,
    )

    return AppResponse(data=result)


@router.delete("/{exercise_set_plan_id}")
async def delete_exercise_set_plan(
    workout_plan_id: int,
    exercise_set_plan_id: int,
    exercise_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetPlanService = Depends(
        get_exercise_set_plan_service
    )
):
    result = await exercise_set_service.delete_set_plan(
        exercise_set_plan_id=exercise_set_plan_id,
        exercise_plan_id=exercise_plan_id,
        workout_plan_id=workout_plan_id,
        user_id=user_data.id,
    )

    return AppResponse(data=result)
