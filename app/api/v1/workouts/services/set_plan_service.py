from sqlalchemy import asc, update
from app.api.v1.schema.workout_plan import ExerciseSetPlanBase
from app.api.v1.workouts.schema import ExerciseSetPlanPagination

from app.api.v1.workouts.utils.order_decorator import validate_set_number
from app.models import ExercisePlan, ExerciseSetPlan, User, WorkoutPlan
from app.repositories import Repos


class ExerciseSetPlanService:
    def __init__(self, repos: Repos):
        self.repos = repos

    @validate_set_number
    async def add_set_to_exercise_plan(
        self, exercise_plan_id: int, payload: ExerciseSetPlanBase, **kwargs
    ):
        payload.exercise_plan_id = exercise_plan_id
        return await self.repos.exercise_set_plan.create(data=payload)

    async def get_one_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ) -> ExerciseSetPlanBase:
        return await self.repos.exercise_set_plan.find_one_exercise_set_plan(
            workout_plan_id=workout_plan_id,
            user_id=user_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
        )

    async def get_many_set_plans(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        pagination: ExerciseSetPlanPagination,
    ):
        base_where_clause = [
            ExerciseSetPlan.exercise_plan_id == ExercisePlan.id,
            ExercisePlan.workout_plan_id == WorkoutPlan.id,
            WorkoutPlan.user_id == User.id,
            User.id == user_id,
            WorkoutPlan.id == workout_plan_id,
            ExercisePlan.id == exercise_plan_id,
        ]
        base_order_clause = [asc(ExerciseSetPlan.set_number)]

        if pagination.skip:
            return await self.repos.exercise_set_plan.get_all(
                where_clause=base_where_clause, order_clause=base_order_clause
            )

        return await self.repos.exercise_set_plan.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[*pagination.filter_fields, *base_where_clause],
            order_clause=[*pagination.sort_fields, *base_order_clause],
        )

    async def delete_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ):
        deleted_set = await self.repos.exercise_set_plan.delete_exercise_set_plan(
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
            user_id=user_id,
            commit=False,
        )

        session = self.repos.session
        old_set_number = deleted_set.set_number

        await session.execute(
            update(ExerciseSetPlan)
            .where(
                ExerciseSetPlan.exercise_plan_id == exercise_plan_id,
                ExerciseSetPlan.set_number > old_set_number,
            )
            .values(set_number=ExerciseSetPlan.set_number - 1)
        )
        await session.commit()

        return deleted_set

    @validate_set_number
    async def update_set_plan(
        self,
        exercise_set_plan_id: int,
        payload: ExerciseSetPlanBase,
        **kwargs,
    ):
        return await self.repos.exercise_set_plan.update_one(
            data=payload,
            where_clause=[ExerciseSetPlan.id == exercise_set_plan_id],
        )
