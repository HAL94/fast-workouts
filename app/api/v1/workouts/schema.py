from typing import ClassVar, Optional
from app.api.v1.schema import WorkoutPlanBase, ExercisePlanBase, ExerciseSetPlanBase
from app.core.common.app_response import AppBaseModel


class WorkoutPlanRead(WorkoutPlanBase):
    # exlcusdes the workout_exercise_plans from the base class
    workout_exercise_plans: ClassVar[list["ExerciseSetPlanBase"]]

    exercises_count: int
    muscle_groups: list[str] = []


# --- Create Workout Schema ---
# Represents creation of workout plan, exercise plans and exercise sets plans
class ExerciseSetPlanCreate(ExerciseSetPlanBase):
    id: ClassVar[int]  # exclusion of id


class ExercisePlanCreate(ExercisePlanBase):
    id: ClassVar[int]  # exclusion of id
    workout_exercise_set_plans: list["ExerciseSetPlanCreate"]


class CreateWorkoutPlanRequest(AppBaseModel):
    title: str
    description: str
    comments: Optional[str] = None
    user_id: Optional[int] = None

    workout_exercise_plans: Optional[list[ExercisePlanCreate]] = None


# --- Update Workout Schema ---
# Represents updation of workout plan, exercise plans and exercise sets plans


class ExerciseSetPlanUpdate(AppBaseModel):
    id: int
    set_number: Optional[int] = None
    target_reps: Optional[int] = None
    target_weight: Optional[float] = None
    target_duration_minutes: Optional[float] = None


class ExercisePlanUpdate(AppBaseModel):
    id: int
    exercise_id: Optional[int]
    order_in_plan: Optional[int]
    target_sets: Optional[int]
    workout_exercise_set_plans: Optional[list["ExerciseSetPlanUpdate"]] = []
    target_duration_minutes: Optional[float] = None
    notes: Optional[str] = None


class UpdateWorkoutPlanRequest(AppBaseModel):
    id: int
    title: Optional[str]
    description: Optional[str] = None
    comments: Optional[str] = None

    workout_exercise_plans: Optional[list[ExercisePlanUpdate]] = []
