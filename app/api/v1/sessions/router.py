
from fastapi import APIRouter, Depends, Query

from app.api.v1.sessions.schema import WorkoutSessionReadPagination
from app.api.v1.sessions.services.workout_session_service import WorkoutSessionService
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_session_service


router: APIRouter = APIRouter(prefix="/sessions")


@router.get("/")
async def get_workout_sessions(
    pagination: WorkoutSessionReadPagination = Query(...),
    user_data: UserRead = Depends(validate_jwt),
    session_service: WorkoutSessionService = Depends(get_session_service)
):
    result = await session_service.get_many_sessions(user_id=user_data.id, pagination=pagination)
    return AppResponse(data=result)
