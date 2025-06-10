from datetime import datetime
from typing import ClassVar, Optional
from app.core.common.app_response import AppBaseModel

class WorkoutPlanBase(AppBaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    comments: Optional[str] = None
    user_id: Optional[int] = None
    workout_exercise_plans: Optional[list["ExercisePlanBase"]] = []
    

class ExercisePlanBase(AppBaseModel):
    id: Optional[int] = None
    exercise_id: int
    order_in_plan: int
    target_sets: int
    target_duration_minutes: Optional[float] = None
    notes: Optional[str] = None
    workout_plan_id: Optional[int] = None
    created_at: Optional[str | datetime] = None
    updated_at: Optional[str | datetime] = None
    workout_exercise_set_plans: Optional[list["ExerciseSetPlanBase"]] = []

class ExerciseSetPlanBase(AppBaseModel):
    id: Optional[int] = None
    set_number: int
    target_reps: int
    target_weight: float
    target_duration_seconds: Optional[int] = None
    workout_exercise_plan_id: Optional[int] = None
    created_at: Optional[str | datetime] = None
    updated_at: Optional[str | datetime] = None
    
class WorkoutPlanRead(WorkoutPlanBase):
    # exlcusdes the workout_exercise_plans from the base class
    workout_exercise_plans: ClassVar[list["ExerciseSetPlanBase"]]
    
    exercises_count: int
    muscle_groups: list[str] = []

class ExercisePlanCreate(ExercisePlanBase):    
    workout_exercise_set_plans: list["ExerciseSetPlanCreate"]

class ExerciseSetPlanCreate(ExerciseSetPlanBase):
   pass

class CreateWorkoutPlanRequest(AppBaseModel):
    title: str
    description: str
    comments: Optional[str] = None
    user_id: Optional[int] = None
    
    workout_exercise_plans: Optional[list[ExercisePlanCreate]] = []

