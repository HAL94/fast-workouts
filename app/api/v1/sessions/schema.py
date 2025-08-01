# --- Paginated Read Schema ---
# Represents pagination schema for workout session, exercise session results and exercise session set results
from app.core.common.pagination_factory import PaginationFactory
from app.models import WorkoutSession, ExerciseResult, ExerciseSetResult
from app.core.common.app_response import AppBaseModel
from typing import Optional

# --- Read Paginated Session Schema ---
# Represents reads of workout session, exercise results and exercise sets results
session_cols = WorkoutSession.columns()
SessionPagination = PaginationFactory.create_pagination(
    WorkoutSession, sortable_fields=session_cols, filterable_fields=session_cols
)
class WorkoutSessionReadPagination(SessionPagination):
    pass

ex_res_cols = ExerciseResult.columns()
ExerciseResultPaginationBase = PaginationFactory.create_pagination(
    ExerciseResult, sortable_fields=ex_res_cols, filterable_fields=ex_res_cols
)
class ExerciseResultPagination(ExerciseResultPaginationBase):
    pass

ex_set_res_cols = ExerciseSetResult.columns()
ExerciseSetResultPaginationBase = PaginationFactory.create_pagination(
    ExerciseSetResult, sortable_fields=ex_set_res_cols, filterable_fields=ex_set_res_cols
)
class ExerciseSetResultPagination(ExerciseSetResultPaginationBase):
    pass



# --- Create Session Schema ---
# Represents creation of workout session, exercise results and exercise sets results
class WorkoutSessionCreate(AppBaseModel):
    workout_plan_id: int


class WorkoutSessionResultCreate(AppBaseModel):
    session_comments: Optional[str] = None
    workout_session_results: list["ExerciseResultCreate"]


class ExerciseResultCreate(AppBaseModel):
    sets_achieved: int
    exercise_set_results: list["SetResultCreate"]
    exercise_plan_id: int
    exercise_id: int

    duration_minutes_achieved: Optional[float]

    workout_session_id: Optional[int] = None


class SetResultCreate(AppBaseModel):
    set_number: int
    reps_achieved: int
    weight_achieved: float
    exercise_set_plan_id: int

    duration_seconds: Optional[int] = None
    rpe: Optional[int] = None

    exercise_result_id: Optional[int] = None


