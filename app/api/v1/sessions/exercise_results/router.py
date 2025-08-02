from fastapi import APIRouter, Depends, Query
from app.core.auth.schema import UserRead
from app.core.auth.jwt import validate_jwt
from app.dependencies.services import get_exercise_result_service
from app.api.v1.sessions.services import ExerciseResultService
from app.api.v1.schema.workout_session import ExerciseResultBase
from app.core.common.app_response import AppResponse
from app.api.v1.sessions.schema import ExerciseResultPagination

from ..exercise_set_results.router import router as set_result_router

router: APIRouter = APIRouter(prefix="/{session_id}/exercises")


@router.post("/")
async def add_result(
    exercise_result: ExerciseResultBase,
    user_data: UserRead = Depends(validate_jwt),
    exercise_result_service: ExerciseResultService = Depends(
        get_exercise_result_service
    ),
):
    result = await exercise_result_service.add_exercise_result(
        user_id=user_data.id, data=exercise_result
    )
    return AppResponse(data=result)


@router.patch("/{exercise_result_id}")
async def update_result(
    exercise_result_id: int,
    exercise_result: ExerciseResultBase,
    user_data: UserRead = Depends(validate_jwt),
    exercise_result_service: ExerciseResultService = Depends(
        get_exercise_result_service
    ),
):
    exercise_result.id = exercise_result_id

    result = await exercise_result_service.update_exercise_result(
        user_id=user_data.id, data=exercise_result
    )
    return AppResponse(data=result)


@router.delete("/{exercise_result_id}")
async def delete_result(
    exercise_result_id: int,
    user_data: UserRead = Depends(validate_jwt),
    exercise_result_service: ExerciseResultService = Depends(
        get_exercise_result_service
    ),
):
    result = await exercise_result_service.remove_exercise_result(
        user_id=user_data.id, exercise_result_id=exercise_result_id
    )

    return AppResponse(data=result)


@router.get("/{exercise_result_id}")
async def get_one_exercise_result(
    exercise_result_id: int,
    user_data: UserRead = Depends(validate_jwt),
    exercise_result_service: ExerciseResultService = Depends(
        get_exercise_result_service
    ),
):
    result = await exercise_result_service.get_one_exercise_result(
        user_id=user_data.id, exercise_result_id=exercise_result_id
    )

    return AppResponse(data=result)


@router.get("/")
async def get_exercise_results(
    session_id: int,
    pagination: ExerciseResultPagination = Query(...),
    user_data: UserRead = Depends(validate_jwt),
    exercise_result_service: ExerciseResultService = Depends(
        get_exercise_result_service
    ),
):
    result = await exercise_result_service.get_many_exercise_results(
        user_id=user_data.id, session_id=session_id, pagination=pagination
    )

    return AppResponse(data=result)

router.include_router(set_result_router)