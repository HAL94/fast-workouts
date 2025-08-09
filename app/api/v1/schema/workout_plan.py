from datetime import datetime, timedelta
from typing import Any, Optional

from pydantic import Field, ValidationInfo, field_validator

from app.core.common.app_response import AppBaseModel
from app.models import ScheduleStatus, WorkoutPlan, ExercisePlan, ExerciseSetPlan


class WorkoutPlanBase(AppBaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    comments: Optional[str] = None
    user_id: Optional[int] = None
    exercise_plans: Optional[list["ExercisePlanBase"]] = None

    class Meta:
        orm_model = WorkoutPlan


class ExercisePlanBase(AppBaseModel):
    id: Optional[int] = None
    exercise_id: int
    order_in_plan: int = Field(min=1, description="Order in the workout plan")
    target_sets: int
    target_duration_minutes: Optional[float] = None
    notes: Optional[str] = None
    workout_plan_id: Optional[int] = None
    created_at: Optional[str | datetime] = None
    updated_at: Optional[str | datetime] = None
    exercise_set_plans: Optional[list["ExerciseSetPlanBase"]] = None

    class Meta:
        orm_model = ExercisePlan


class ExerciseSetPlanBase(AppBaseModel):
    id: Optional[int] = None
    set_number: int = Field(min=1, description="Order in the exercise plan")
    target_reps: int
    target_weight: float
    target_duration_seconds: Optional[int] = None
    exercise_plan_id: Optional[int] = None
    created_at: Optional[str | datetime] = None
    updated_at: Optional[str | datetime] = None

    class Meta:
        orm_model = ExerciseSetPlan


class ScheduleBase(AppBaseModel):
    id: Optional[int] = None
    workout_plan_id: int
    user_id: int
    start_at: datetime
    end_at: Optional[datetime] = None
    remind_before_minutes: Optional[float] = None
    reminder_send_status: ScheduleStatus = Field(default=ScheduleStatus.pending)
    reminder_send_time: Optional[datetime] = None  # actual time when reminder was sent
    reminder_scheduled_send_time: Optional[datetime] = (
        None  # schedule time when reminder shuld be sent
    )
    auto_start_session: Optional[bool] = None

    @field_validator("reminder_scheduled_send_time", mode="after")
    @classmethod
    def init_reminder_scheduled_send_time(cls, v: Any, info: ValidationInfo):
        start_at: datetime = info.data.get("start_at")
        remind_before_minutes = info.data.get("remind_before_minutes")

        if start_at and remind_before_minutes:
            reminder_time = start_at - timedelta(minutes=remind_before_minutes)
            return reminder_time
        return v
