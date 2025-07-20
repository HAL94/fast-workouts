from datetime import datetime
from typing import Optional
from app.api.v1.schema.workout_plan import ExercisePlanBase, WorkoutPlanBase, ExerciseSetPlanBase
from app.core.common.app_response import AppBaseModel



class WorkoutSessionBase(AppBaseModel):
    id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    session_comments: Optional[str] = None
    schedule_id: Optional[int] = None
    
    workout_plan: Optional[WorkoutPlanBase] = None
    workout_session_results: Optional[list["ExerciseResultBase"]] = None

class ExerciseResultBase(AppBaseModel):
    id: Optional[int] = None
    sets_achieved: int
    duration_minutes_achieved: Optional[float]
    workout_session_id: int
    
    exercise_plan: Optional[ExercisePlanBase] = None
    exercise_set_results: Optional[list["ExerciseSetResult"]] = None
    
class ExerciseSetResult(AppBaseModel):
    id: Optional[int] = None
    set_number: int
    reps_achieved: int
    weight_achieved: float
    duration_seconds: Optional[int] = None
    rpe: Optional[int] = None
    
    exercise_result_id: int
    exercise_set_plan: Optional[ExerciseSetPlanBase] = None