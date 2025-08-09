from fastapi import APIRouter, Depends, Query

from app.api.v1.sessions.schema import (
    WorkoutSessionPagination,
    WorkoutSessionCreate,
)
from app.api.v1.sessions.services.workout_session_service import WorkoutSessionService
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_session_service
from .schema import WorkoutSessionResultCreate
from app.api.v1.sessions.exercise_results.router import router as exercise_result_router

router: APIRouter = APIRouter(prefix="/sessions")


@router.get("/")
async def get_workout_sessions(
    pagination: WorkoutSessionPagination = Query(...),
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.get_many_sessions(
        user_id=user_data.id, pagination=pagination
    )
    return AppResponse(data=result)


@router.get("/{session_id}")
async def get_workout_session(
    session_id: int,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.get_one_session(
        user_id=user_data.id, session_id=session_id
    )
    return AppResponse(data=result)


@router.post("/start")
async def create_session(
    payload: WorkoutSessionCreate,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.start_session_now(
        user_id=user_data.id, payload=payload
    )
    return AppResponse(data=result)


@router.post("/end/{session_id}")
async def end_session(
    session_id: int,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.end_session_now(
        user_id=user_data.id, session_id=session_id
    )

    return AppResponse(data=result)


@router.post("/{session_id}/results")
async def record_session_results(
    session_id: int,
    workout_results: WorkoutSessionResultCreate,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.create_session_results(
        user_id=user_data.id, session_id=session_id, workout_results=workout_results
    )
    return AppResponse(data=result)


router.include_router(exercise_result_router)


@router.get("/{session_id}/report")
async def generate_workout_report(
    session_id: int,
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    result = await session_service.get_workout_report(
        session_id=session_id, user_id=user_data.id
    )

    return AppResponse(data=result)
