from fastapi import APIRouter, Depends, Query
from app.api.v1.schema.workout_session import ExerciseSetResultBase
from app.dependencies.services import get_exercise_set_result_service
from app.api.v1.sessions.services import ExerciseSetResultService
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.core.auth.jwt import validate_jwt
from app.api.v1.sessions.schema import ExerciseSetResultPagination

router: APIRouter = APIRouter(prefix="/{exercise_result_id}/sets")


@router.post("/")
async def create_exercise_set_result(
    exercise_result_id: int,
    exercise_set_result_data: ExerciseSetResultBase,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetResultService = Depends(
        get_exercise_set_result_service
    ),
):
    result = await exercise_set_service.add_exercise_set_result(
        user_id=user_data.id,
        exercise_result_id=exercise_result_id,
        data=exercise_set_result_data,
    )

    return AppResponse(data=result)


@router.get("/")
async def get_exercise_set_results(
    exercise_result_id: int,
    pagination: ExerciseSetResultPagination = Query(...),
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetResultService = Depends(
        get_exercise_set_result_service
    ),
):
    result = await exercise_set_service.get_many_exercise_set_results(
        pagination=pagination,
        exercise_result_id=exercise_result_id,
        user_id=user_data.id,
    )

    return AppResponse(data=result)


@router.get("/{set_result_id}")
async def get_one_result_set(
    exercise_result_id: int,
    set_result_id: int,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetResultService = Depends(
        get_exercise_set_result_service
    ),
):
    result = await exercise_set_service.get_one_exercise_set_result(
        set_result_id=set_result_id,
        exercise_result_id=exercise_result_id,
        user_id=user_data.id,
    )

    return AppResponse(data=result)


@router.patch("/{set_result_id}")
async def update_set_result(
    exercise_result_id: int,
    set_result_id: int,
    data: ExerciseSetResultBase,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetResultService = Depends(
        get_exercise_set_result_service
    ),
):
    result = await exercise_set_service.update_one_exercise_set_result(
        user_id=user_data.id,
        exercise_result_id=exercise_result_id,
        set_result_id=set_result_id,
        data=data,
    )

    return AppResponse(data=result)


@router.delete("/{set_result_id}")
async def delete_set_result(
    exercise_result_id: int,
    set_result_id: int,
    user_data: UserRead = Depends(validate_jwt),
    exercise_set_service: ExerciseSetResultService = Depends(
        get_exercise_set_result_service
    ),
):
    result = await exercise_set_service.delete_one_set_result(
        exercise_result_id=exercise_result_id,
        set_result_id=set_result_id,
        user_id=user_data.id,
    )

    return AppResponse(data=result)
