from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
import pytz

from app.api.v1.workouts.schema import (
    CreateWorkoutScheduleRequest,
    GetScheduleReminderSuggestionsRequest,
    ScheduleCreateResponse,
    ScheduleSuggestionsResponse,
    WorkoutPlanScheduleReadPagination,
)
from app.api.v1.workouts.services import WorkoutScheduleService
from app.api.v1.workouts.utils.date_formatter import format_to_local_time
from app.api.v1.workouts.utils.schedule_time_validator import TimeReminderSuggestion
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_schedule_service
from app.worker.tasks import reminder_email

router: APIRouter = APIRouter(
    prefix="/{workout_plan_id}/schedules", dependencies=[Depends(validate_jwt)]
)


@router.get("/")
async def get_workout_plan_schedules(
    workout_plan_id: int,
    user_data: UserRead = Depends(validate_jwt),
    pagination: WorkoutPlanScheduleReadPagination = Query(...),
    workout_schedule_service: WorkoutScheduleService = Depends(
        get_schedule_service),
):
    result = await workout_schedule_service.get_many_workout_schedules(
        user_id=user_data.id, pagination=pagination, workout_plan_id=workout_plan_id
    )
    print(f"{datetime.now().isoformat()}")

    return AppResponse(data=result)


@router.get("/suggestions")
async def get_schedule_reminder_suggestions(
    payload: GetScheduleReminderSuggestionsRequest
):
    suggestions = TimeReminderSuggestion.get_reminder_suggestions(
        payload.start_at)

    data = ScheduleSuggestionsResponse.model_validate(suggestions)

    return AppResponse(data=data)


@router.get("/{workout_plan_schedule_id}")
async def get_workout_plan_schedule(
    workout_plan_id: int,
    workout_plan_schedule_id: int,
    user_data: UserRead = Depends(validate_jwt),
    workout_schedule_service: WorkoutScheduleService = Depends(
        get_schedule_service),
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
    workout_plan_service: WorkoutScheduleService = Depends(
        get_schedule_service),
):
    result = await workout_plan_service.create_workout_schedule(
        user_id=user_data.id,
        workout_plan_id=workout_plan_id,
        payload=payload,
    )
    reminder_time = payload.start_at - \
        timedelta(minutes=payload.remind_before_minutes)
    result = ScheduleCreateResponse(
        **result.model_dump(), reminder_send_time=format_to_local_time(reminder_time))

    if payload.remind_before_minutes:
        start_at_utc = pytz.UTC.localize(
            payload.start_at) if not payload.start_at.tzinfo else payload.start_at
        reminder_email.apply_async(
            (result.id,), eta=start_at_utc - timedelta(minutes=payload.remind_before_minutes))
    return AppResponse(data=result)
