from datetime import timedelta
from fastapi import APIRouter, Depends, Query
import pytz

from app.api.v1.schema.workout_session import WorkoutSessionBase
from app.api.v1.sessions.services.workout_session_service import WorkoutSessionService
from app.api.v1.workouts.schema import (
    CreateWorkoutScheduleRequest,
    GetScheduleReminderSuggestionsRequest,
    ScheduleCreateResponse,
    ScheduleSuggestionsResponse,
    WorkoutPlanSchedulePagination,
)
from app.api.v1.workouts.services import WorkoutScheduleService
from app.api.v1.workouts.utils.schedule_time_validator import TimeReminderSuggestion
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_schedule_service, get_session_service
from app.models import ScheduleStatus, WorkoutSessionStatus
from app.worker.tasks import reminder_email
from app.worker.tasks.auto_start_session import start_scheduled_session

router: APIRouter = APIRouter(
    prefix="/{workout_plan_id}/schedules", dependencies=[Depends(validate_jwt)]
)


@router.get("/")
async def get_workout_plan_schedules(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    pagination: WorkoutPlanSchedulePagination = Query(...),
    workout_schedule_service: WorkoutScheduleService = Depends(get_schedule_service),
):
    result = await workout_schedule_service.get_many_workout_schedules(
        user_id=user_data.id, pagination=pagination, workout_plan_id=workout_plan_id
    )
    return AppResponse(data=result)


@router.get("/suggestions")
async def get_schedule_reminder_suggestions(
    payload: GetScheduleReminderSuggestionsRequest,
):
    suggestions = TimeReminderSuggestion.get_reminder_suggestions(payload.start_at)

    data = ScheduleSuggestionsResponse.model_validate(suggestions)

    return AppResponse(data=data)


@router.get("/{workout_plan_schedule_id}")
async def get_workout_plan_schedule(
    workout_plan_id: int,
    workout_plan_schedule_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_schedule_service: WorkoutScheduleService = Depends(get_schedule_service),
):
    result = await workout_schedule_service.get_workout_schedule(
        user_id=user_data.id,
        workout_plan_id=workout_plan_id,
        workout_plan_schedule_id=workout_plan_schedule_id,
    )
    return AppResponse(data=result)


@router.post("/")
async def create_workout_plan_schedule(
    workout_plan_id: int,
    payload: CreateWorkoutScheduleRequest,
    user_data: UserRead = Depends(validate_jwt),
    workout_plan_service: WorkoutScheduleService = Depends(get_schedule_service),
    session_service: WorkoutSessionService = Depends(get_session_service),
):
    should_remind = payload.remind_before_minutes is not None

    if not should_remind:
        payload.reminder_status = ScheduleStatus.unset

    result = await workout_plan_service.create_workout_schedule(
        user_id=user_data.id,
        workout_plan_id=workout_plan_id,
        payload=payload,
    )

    result = ScheduleCreateResponse(**result.model_dump())

    start_at_utc = (
        pytz.UTC.localize(payload.start_at)
        if not payload.start_at.tzinfo
        else payload.start_at
    )
    if should_remind:
        # send reminder email
        reminder_email.apply_async(
            (result.id,),
            eta=start_at_utc - timedelta(minutes=payload.remind_before_minutes),
        )

    created_workout_session = await session_service.schedule_session(
        payload=WorkoutSessionBase(
            workout_plan_id=workout_plan_id,
            user_id=user_data.id,
            schedule_id=result.id,
            status=WorkoutSessionStatus.scheduled,
        ),
    )

    if payload.auto_start_session:
        session_id = created_workout_session.id
        start_scheduled_session.apply_async((session_id,), eta=start_at_utc)

    return AppResponse(data=result)
