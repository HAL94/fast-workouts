from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest,
    WorkoutPlanBase,
)
from app.core.database.base_repo import BaseRepo
from app.models import (
    ExerciseMuscleGroup,
    MuscleGroup,
    WorkoutExercisePlan,
    WorkoutPlan,
)
from app.repositories.exercise_plan_repository import ExercisePlanRepository
from app.repositories.exercise_set_plan_repository import ExerciseSetPlanRepository


class WorkoutPlanRepository(BaseRepo[WorkoutPlan, WorkoutPlanBase]):
    __dbmodel__ = WorkoutPlan
    __model__ = WorkoutPlanBase

    def __init__(
        self,
        session: AsyncSession,
        exercise_plan_repo: ExercisePlanRepository,
        exercise_set_plan_repo: ExerciseSetPlanRepository,
    ):
        super().__init__(session)
        self.exercise_plan_repo = exercise_plan_repo
        self.exercise_set_plan_repo = exercise_set_plan_repo

    async def get_workout_by_id(self, workout_id: int) -> WorkoutPlanBase:
        session = self.session
        workout_plan_cursor = await session.scalars(
            select(WorkoutPlan)
            .where(WorkoutPlan.id == workout_id)
            .options(
                selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
                    WorkoutExercisePlan.workout_exercise_set_plans
                )
            )
        )

        fully_loaded_workout_plan = workout_plan_cursor.unique().first()

        return fully_loaded_workout_plan

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

    async def update_workout_plan(
        self, user_id: int, workout_plan_id: int, update_data: UpdateWorkoutPlanRequest
    ) -> WorkoutPlanBase:
        workout_data = await self.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        workout_plan = WorkoutPlanBase(
            title=update_data.title or workout_data.title,
            description=update_data.description or workout_data.description,
            user_id=user_id,
            comments=update_data.comments or workout_data.comments,
        )
        await self.update_one(
            data=workout_plan,
            where_clause=[
                WorkoutPlan.id == workout_plan_id,
                WorkoutPlan.user_id == user_id,
            ],
        )

        await self.exercise_plan_repo.update_many(update_data.workout_exercise_plans)

        for exercise_plan in update_data.workout_exercise_plans:
            await self.exercise_set_plan_repo.update_many(
                data=exercise_plan.workout_exercise_set_plans,
            )

        fully_loaded_workout_plan = await self.get_workout_by_id(
            workout_id=workout_plan_id
        )

        return WorkoutPlanBase.model_validate(
            fully_loaded_workout_plan, from_attributes=True
        )

    async def create_workout_plan(
        self, user_id: int, workout_data: CreateWorkoutPlanRequest
    ) -> WorkoutPlanBase:
        workout_data_create = WorkoutPlanBase(
            title=workout_data.title,
            description=workout_data.description,
            user_id=user_id,
            comments=workout_data.comments,
        )

        created_workout_data = await self.create(data=workout_data_create)

        created_exercises = await self.exercise_plan_repo.create_many_exercise_plans(
            workout_id=created_workout_data.id,
            payload=workout_data.workout_exercise_plans,
        )

        for index, exercise_set_plan in enumerate(created_exercises):
            data = workout_data.workout_exercise_plans[index]

            await self.exercise_set_plan_repo.create_many_exercise_set_plans(
                exercise_plan_id=exercise_set_plan.id,
                payload=data.workout_exercise_set_plans,
            )

        fully_loaded_workout_plan = await self.get_workout_by_id(
            workout_id=created_workout_data.id
        )

        return WorkoutPlanBase.model_validate(
            fully_loaded_workout_plan, from_attributes=True
        )

    async def get_exercise_count_for_workout(self, workout_id: int) -> int:
        exercises_count_stmt = select(func.count()).select_from(
            select(WorkoutExercisePlan)
            .where(WorkoutExercisePlan.workout_plan_id == workout_id)
            .subquery()
        )

        return await self.session.scalar(exercises_count_stmt)

    async def delete_workout_plan(self, workout_plan_id: int, user_id: int):
        return await self.delete_one(
            val=workout_plan_id,
            where_clause=[
                WorkoutPlan.id == workout_plan_id,
                WorkoutPlan.user_id == user_id,
            ]
        )
