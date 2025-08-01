from fastapi import APIRouter, Depends, Query
from app.core.auth.schema import UserRead
from app.core.auth.jwt import validate_jwt
from app.dependencies.services import get_session_service, WorkoutSessionService
from app.api.v1.schema.workout_session import ExerciseResultBase
from app.core.common.app_response import AppResponse
from app.api.v1.sessions.schema import ExerciseResultPagination

router: APIRouter = APIRouter(prefix="/{session_id}/exercises")


@router.post("/")
async def add_result(
    exercise_result: ExerciseResultBase,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.add_exercise_result(
        user_id=user_data.id, data=exercise_result
    )
    return AppResponse(data=result)


@router.patch("/{exercise_result_id}")
async def update_result(
    exercise_result_id: int,
    exercise_result: ExerciseResultBase,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    exercise_result.id = exercise_result_id

    result = await session_service.update_exercise_result(
        user_id=user_data.id, data=exercise_result
    )
    return AppResponse(data=result)


@router.delete("/{exercise_result_id}")
async def delete_result(
    exercise_result_id: int,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.remove_exercise_result(
        user_id=user_data.id, exercise_result_id=exercise_result_id
    )

    return AppResponse(data=result)


@router.get("/{exercise_result_id}")
async def get_one_exercise_result(
    exercise_result_id: int,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.get_one_exercise_result(
        user_id=user_data.id, exercise_result_id=exercise_result_id
    )

    return AppResponse(data=result)


@router.get("/")
async def get_exercise_results(
    session_id: int,
    pagination: ExerciseResultPagination = Query(...),
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.get_many_exercise_results(
        user_id=user_data.id, session_id=session_id, pagination=pagination
    )

    return AppResponse(data=result)
