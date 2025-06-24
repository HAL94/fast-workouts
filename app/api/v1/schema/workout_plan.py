from datetime import datetime
from typing import Optional

from pydantic import Field
from app.core.common.app_response import AppBaseModel


class WorkoutPlanBase(AppBaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    comments: Optional[str] = None
    user_id: Optional[int] = None
    workout_exercise_plans: Optional[list["ExercisePlanBase"]] = None


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
    workout_exercise_set_plans: Optional[list["ExerciseSetPlanBase"]] = None


class ExerciseSetPlanBase(AppBaseModel):
    id: Optional[int] = None
    set_number: int = Field(min=1, description="Order in the exercise plan")
    target_reps: int
    target_weight: float
    target_duration_seconds: Optional[int] = None
    workout_exercise_plan_id: Optional[int] = None
    created_at: Optional[str | datetime] = None
    updated_at: Optional[str | datetime] = None


class ScheduleBase(AppBaseModel):
    id: Optional[int] = None
    workout_plan_id: int
    user_id: int
    start_at: datetime
    end_time: Optional[datetime] = None
    remind_before_minutes: Optional[int] = None
