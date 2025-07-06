from datetime import datetime
from typing import ClassVar, Optional, Self

from pydantic import model_validator
import pytz

from app.api.v1.schema import WorkoutPlanBase, ExercisePlanBase, ExerciseSetPlanBase
from app.api.v1.schema.workout_plan import ScheduleBase
from app.api.v1.workouts.utils.schedule_time_validator import TimeValidation
from app.core.common.app_response import AppBaseModel
from app.core.common.pagination_factory import PaginationFactory
from app.models import (
    WorkoutExercisePlan,
    WorkoutExerciseSetPlan,
    WorkoutPlan,
    WorkoutPlanSchedule,
)

# --- Paginated Read Schema ---
# Represents pagination schema for workout plans, exercise plans and exercise sets plans
workout_plan_cols = WorkoutPlan.columns()
WorkoutPlanPagination = PaginationFactory.create_pagination(
    WorkoutPlan,
    sortable_fields=workout_plan_cols, filterable_fields=workout_plan_cols
)
class WorkoutPlanReadPagination(WorkoutPlanPagination):
    pass


exercise_plan_cols = WorkoutExercisePlan.columns()
WorkoutExercisePlanPagination = PaginationFactory.create_pagination(WorkoutExercisePlan,
                                                                    sortable_fields=exercise_plan_cols, filterable_fields=exercise_plan_cols
                                                                    )


class ExercisePlanReadPagination(WorkoutExercisePlanPagination):
    pass


exercise_set_plan_cols = WorkoutExerciseSetPlan.columns()
ExerciseSetPlanPagination = PaginationFactory.create_pagination(WorkoutExerciseSetPlan,
                                                                sortable_fields=exercise_set_plan_cols, filterable_fields=exercise_set_plan_cols
                                                                )


class ExerciseSetPlanReadPagination(ExerciseSetPlanPagination):
    pass


workout_schedule_cols = WorkoutPlanSchedule.columns()
WorkoutPlanSchedulePagination = PaginationFactory.create_pagination(WorkoutPlanSchedule,
                                                                    sortable_fields=workout_schedule_cols, filterable_fields=workout_schedule_cols
                                                                    )
class WorkoutPlanScheduleReadPagination(WorkoutPlanSchedulePagination):
    pass


# --- Read Workout Schema ---
# Represents reading workout plans, exercise plans and exercise sets plans
class WorkoutPlanReadPaginatedItem(WorkoutPlanBase):
    # excludes the workout_exercise_plans from the base class
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


class CreateWorkoutScheduleRequest(ScheduleBase):
    workout_plan_id: ClassVar[int]  # exclusion of id
    user_id: ClassVar[int]  # exclusion of user_id

    @model_validator(mode="after")
    def validate_start_time_and_reminder(self,) -> Self:
        start_at: Optional[datetime] = self.start_at
        end_time: Optional[datetime] = self.end_time

        remind_before_minutes: Optional[float] = self.remind_before_minutes

        if not start_at:
            raise ValueError("start_at value was not passed")

        start_at_validation = TimeValidation.is_valid_start_datetime(start_at)

        if start_at_validation.get("max_reached"):
            raise ValueError("Maximum reached")
        elif start_at_validation.get("is_in_past"):
            raise ValueError("Start time will be in the past")
        elif start_at_validation.get("is_too_early"):
            raise ValueError(
                f"Start time is too early. Need to set schedule at least after: {TimeValidation.REMINDER_LIMITS.get("MIN_SCHEDULE_START_TIME")} from now. Consider starting session now!")

        start_at_utc = pytz.UTC.localize(
            start_at) if not start_at.tzinfo else start_at

        if end_time:
            end_time_utc = pytz.UTC.localize(
                end_time) if not end_time.tzinfo else end_time

            if end_time_utc < start_at_utc:
                raise ValueError(
                    f"Passed value for end_time {end_time_utc} is before start_at: {start_at_utc}")

        if remind_before_minutes is not None:
            """
                checks the following for reminder:
                - is remind_before_minutes is in the past?
                - is remind_before_minutes too early or too late? Definition of "too late" or "too early":
                    - too late? < 5 minutes before workout start.
                    - too early? < {buffer_time} minutes after current date/time, where buffer_time is set to 5

            """
            validation_result = TimeValidation.validate_excessive_reminder(
                start_at=start_at_utc, remind_before_minutes=remind_before_minutes)
            print("Validation of start_at and remind_before_minutes",
                  validation_result)
            if not validation_result["is_valid"]:
                raise ValueError(*validation_result["errors"])

        return self


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


# --- Get Schedule Suggestion Schema ---
# Represents fetching suggestions for a schedule given a start date/time
class GetScheduleReminderSuggestionsRequest(AppBaseModel):
    start_at: datetime


class ScheduleReminderSuggestionItem(AppBaseModel):
    unit: str
    value: int


class ScheduleSuggestionsResponse(AppBaseModel):
    suggestions: list[ScheduleReminderSuggestionItem] = []


class ScheduleCreateResponse(ScheduleBase):
    reminder_send_time: datetime
