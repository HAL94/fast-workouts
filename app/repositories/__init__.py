from functools import cached_property
from sqlalchemy.ext.asyncio import AsyncSession
from .workout_plan_repository import WorkoutPlanRepository
from .exercise_plan_repository import ExercisePlanRepository
from .exercise_set_plan_repository import ExerciseSetPlanRepository
from .workout_schedule_repository import WorkoutScheduleRepository

all_repos = [
    WorkoutPlanRepository,
    ExercisePlanRepository,
    ExerciseSetPlanRepository,
    WorkoutScheduleRepository,
]
__all__ = all_repos


class Repos:
    def __init__(self, session: AsyncSession):
        self.session = session

    @cached_property
    def workout_plan(self) -> WorkoutPlanRepository:
        return WorkoutPlanRepository(session=self.session)

    @cached_property
    def exercise_plan(self) -> ExercisePlanRepository:
        return ExercisePlanRepository(session=self.session)

    @cached_property
    def exercise_set_plan(self) -> ExerciseSetPlanRepository:
        return ExerciseSetPlanRepository(session=self.session)

    @cached_property
    def workout_schedule(self) -> WorkoutScheduleRepository:
        return WorkoutScheduleRepository(session=self.session)
