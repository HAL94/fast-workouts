from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.v1.schema.workout_plan import ExercisePlanBase, ExerciseSetPlanBase
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
    WorkoutExerciseSetPlan,
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

        fully_loaded_workout_plan = await self.get_one(
            val=workout_plan_id,
            where_clause=[WorkoutPlan.id == workout_plan_id],
            relations=[
                selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
                    WorkoutExercisePlan.workout_exercise_set_plans
                )
            ],
        )

        return fully_loaded_workout_plan

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

        fully_loaded_workout_plan = await self.get_one(
            val=created_workout_data.id,
            where_clause=[WorkoutPlan.id == created_workout_data.id],
            relations=[
                selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
                    WorkoutExercisePlan.workout_exercise_set_plans
                )
            ],
        )

        return fully_loaded_workout_plan

    async def get_workout_exercise_plans(self, user_id: int, workout_plan_id: int):
        await self.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        return await self.exercise_plan_repo.get_many(
            page=1,
            size=10,
            where_clause=[WorkoutExercisePlan.workout_plan_id == workout_plan_id],
        )

    async def get_one_workout_exercise_plan(
        self, user_id: int, workout_plan_id: int, exercise_plan_id: int
    ):
        await self.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        return await self.exercise_plan_repo.get_one(
            val=exercise_plan_id,
            where_clause=[WorkoutExercisePlan.workout_plan_id == workout_plan_id],
        )

    async def get_one_exercise_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ):
        await self.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        return await self.exercise_set_plan_repo.get_one(
            val=exercise_set_plan_id,
            where_clause=[
                WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id
            ],
        )

    async def get_workout_exercise_set_plans(
        self, user_id: int, workout_plan_id: int, exercise_plan_id: int
    ):
        await self.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        await self.exercise_plan_repo.get_one(
            val=exercise_plan_id,
            where_clause=[WorkoutExercisePlan.workout_plan_id == workout_plan_id],
        )
        return await self.exercise_set_plan_repo.get_many(
            page=1,
            size=10,
            where_clause=[
                WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id
            ],
        )

    async def create_workout_exercise_plan(
        self, workout_plan_id: int, user_id: int, payload: ExercisePlanBase
    ) -> ExercisePlanBase:
        await self.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        payload.workout_plan_id = workout_plan_id
        exercise_plan = await self.exercise_plan_repo.create(payload=payload)
        return exercise_plan

    async def create_exercise_set_plan(
        self,
        exercise_plan_id: int,
        workout_plan_id: int,
        user_id: int,
        payload: ExerciseSetPlanBase,
    ):
        await self.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        await self.exercise_plan_repo.get_one(
            val=exercise_plan_id,
            where_clause=[WorkoutExercisePlan.workout_plan_id == workout_plan_id],
        )
        payload.workout_exercise_plan_id = exercise_plan_id
        return await self.exercise_set_plan_repo.create(data=payload)

    async def update_exercise_set_plan(
        self,
        exercise_set_plan_id: int,
        exercise_plan_id: int,
        workout_plan_id: int,
        user_id: int,
        payload: ExerciseSetPlanBase,
    ):
        await self.exercise_set_plan_repo.find_one_exercise_set_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
        )
        return await self.exercise_set_plan_repo.update_one(
            data=payload,
            where_clause=[WorkoutExerciseSetPlan.id == exercise_set_plan_id],
        )

    async def update_workout_exercise_plan(
        self,
        workout_plan_id: int,
        exercise_plan_id: int,
        user_id: int,
        payload: ExercisePlanBase,
    ) -> ExercisePlanBase:
        await self.exercise_plan_repo.find_one_exercise_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
        )
        exercise_plan = await self.exercise_plan_repo.update_one(
            payload,
            where_clause=[
                WorkoutExercisePlan.id == exercise_plan_id,
                WorkoutExercisePlan.workout_plan_id == workout_plan_id,
            ],
        )
        return exercise_plan

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
            ],
        )

    async def delete_workout_exercise_plan(
        self, workout_plan_id: int, user_id: int, exercise_plan_id: int
    ):
        return await self.exercise_plan_repo.delete_exercise_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
        )

    async def delete_workout_exercise_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ):
        return await self.exercise_set_plan_repo.delete_exercise_set_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
        )
