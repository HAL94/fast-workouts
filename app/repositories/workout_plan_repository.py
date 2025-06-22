from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.workouts.schema import (
    WorkoutPlanBase,
)
from app.core.database.base_repo import BaseRepo
from app.models import (
    ExerciseMuscleGroup,
    MuscleGroup,
    WorkoutExercisePlan,
    WorkoutPlan,
)


class WorkoutPlanRepository(BaseRepo[WorkoutPlan, WorkoutPlanBase]):
    __dbmodel__ = WorkoutPlan
    __model__ = WorkoutPlanBase

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)

    async def get_muscles_for_workout(self, workout_id: int) -> list[str]:
        muscles_for_plan = await self.session.scalars(
            select(MuscleGroup.muscle_target)
            .join(
                ExerciseMuscleGroup,
                ExerciseMuscleGroup.muscle_group_id == MuscleGroup.id,
            )
            .join(
                WorkoutExercisePlan,
                ExerciseMuscleGroup.exercise_id == WorkoutExercisePlan.exercise_id,
            )
            .where(WorkoutExercisePlan.workout_plan_id == workout_id)
            .group_by(MuscleGroup.muscle_target)
        )

        return muscles_for_plan.all()

    
    async def get_exercise_count_for_workout(self, workout_id: int) -> int:
        exercises_count_stmt = select(func.count()).select_from(
            select(WorkoutExercisePlan)
            .where(WorkoutExercisePlan.workout_plan_id == workout_id)
            .subquery()
        )

        return await self.session.scalar(exercises_count_stmt)