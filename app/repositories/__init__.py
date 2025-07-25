from functools import cached_property
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.exercise_repository import ExerciseRepository
from .workout_plan_repository import WorkoutPlanRepository
from .exercise_plan_repository import ExercisePlanRepository
from .exercise_set_plan_repository import ExerciseSetPlanRepository
from .workout_schedule_repository import WorkoutScheduleRepository
from .muscle_group_repository import MuscleGroupRepository
from .category_repository import CategoryRepository
from .workout_session_repository import WorkoutSessionRepository
from .exercise_result_repository import ExerciseResultRepository
from .exercise_set_result_repository import ExerciseResultSetRepository

all_repos = [
    WorkoutPlanRepository,
    ExercisePlanRepository,
    ExerciseSetPlanRepository,
    WorkoutScheduleRepository,
    ExerciseRepository,
    MuscleGroupRepository,
    CategoryRepository,
    WorkoutSessionRepository,
    ExerciseResultRepository,
    ExerciseResultSetRepository,
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

    @cached_property
    def exercise(self) -> ExerciseRepository:
        return ExerciseRepository(session=self.session)

    @cached_property
    def muscle_group(self) -> MuscleGroupRepository:
        return MuscleGroupRepository(session=self.session)

    @cached_property
    def category(self) -> CategoryRepository:
        return CategoryRepository(session=self.session)

    @cached_property
    def workout_session(self) -> WorkoutSessionRepository:
        return WorkoutSessionRepository(session=self.session)

    @cached_property
    def exercise_result(self) -> ExerciseResultRepository:
        return ExerciseResultRepository(session=self.session)

    @cached_property
    def exercise_set_result(self) -> ExerciseResultSetRepository:
        return ExerciseResultSetRepository(session=self.session)
