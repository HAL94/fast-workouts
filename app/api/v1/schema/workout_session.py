from datetime import datetime
from typing import Optional

# from app.api.v1.schema.workout_plan import (
#     ExercisePlanBase,
# )
from app.core.common.app_response import AppBaseModel
from app.models import WorkoutSession, ExerciseResult, ExerciseSetResult


class WorkoutSessionBase(AppBaseModel):
    id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    session_comments: Optional[str] = None
    schedule_id: Optional[int] = None
    user_id: int
    workout_plan_id: int

    workout_session_results: Optional[list["ExerciseResultBase"]] = None

    class Meta:
        orm_model = WorkoutSession


class ExerciseResultBase(AppBaseModel):
    id: Optional[int] = None
    sets_achieved: int
    duration_minutes_achieved: Optional[float]
    workout_session_id: int
    exercise_id: int
    exercise_plan_id: int

    # exercise_plan: Optional[ExercisePlanBase] = None
    exercise_set_results: Optional[list["ExerciseSetResultBase"]] = None

    class Meta:
        orm_model = ExerciseResult


class ExerciseSetResultBase(AppBaseModel):
    id: Optional[int] = None
    set_number: int
    reps_achieved: int
    weight_achieved: float
    duration_seconds: Optional[int] = None
    rpe: Optional[int] = None
    exercise_set_plan_id: int

    exercise_result_id: Optional[int] = None

    class Meta:
        orm_model = ExerciseSetResult
