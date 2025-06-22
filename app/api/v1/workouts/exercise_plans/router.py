from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.workouts.service import WorkoutPlanService

from .background_tasks import (
    fix_exercise_set_plan_sequence,
)
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.database import get_async_session
from app.dependencies.services import get_workout_plan_service


router: APIRouter = APIRouter(prefix="/{workout_plan_id}/exercise-plans")


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


@router.delete("/{exercise_plan_id}/exercise_set_plans/{exercise_set_plan_id}")
async def delete_exercise_set_plan(
    workout_plan_id: int,
    exercise_set_plan_id: int,
    exercise_plan_id: int,
    background_tasks: BackgroundTasks,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutPlanService = Depends(get_workout_plan_service),
    session: AsyncSession = Depends(get_async_session),
):
    background_tasks.add_task(
        fix_exercise_set_plan_sequence,
        session=session,
        exercise_plan_id=exercise_plan_id,
    )

    result = await workout_plan_service.delete_exercise_set_plan(
        exercise_set_plan_id=exercise_set_plan_id,
        exercise_plan_id=exercise_plan_id,
        workout_plan_id=workout_plan_id,
        user_id=user_data.id,
    )

    return AppResponse(data=result)
