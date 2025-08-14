from sqlalchemy import asc, select, update
from sqlalchemy.orm import selectinload
from app.api.v1.schema.workout_plan import ExercisePlanBase
from app.api.v1.workouts.schema import ExercisePlanPagination
from app.api.v1.workouts.utils.order_decorator import validate_order_in_plan_number
from app.models import ExercisePlan, User, WorkoutPlan
from app.repositories import Repos


class ExercisePlanService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_exercise_plans(
        self,
        workout_plan_id: int,
        user_id: int,
        pagination: ExercisePlanPagination,
    ):
        base_where_clause = [
            ExercisePlan.workout_plan_id == WorkoutPlan.id,
            WorkoutPlan.user_id == User.id,
            User.id == user_id,
            WorkoutPlan.id == workout_plan_id,
        ]
        base_order_clause = [asc(ExercisePlan.order_in_plan)]

        if pagination.skip:
            return await self.repos.exercise_plan.get_all(
                where_clause=base_where_clause, order_clause=base_order_clause
            )

        return await self.repos.exercise_plan.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[*pagination.filter_fields, *base_where_clause],
            order_clause=[*pagination.sort_fields, *base_order_clause],
        )

    @validate_order_in_plan_number
    async def update_exercise_plan(
        self,
        workout_plan_id: int,
        exercise_plan_id: int,
        user_id: int,
        payload: ExercisePlanBase,
    ):
        exercise_plan = await self.repos.session.scalar(
            select(ExercisePlan)
            .where(ExercisePlan.id == exercise_plan_id)
            .join(WorkoutPlan, ExercisePlan.workout_plan_id == WorkoutPlan.id)
            .where(
                WorkoutPlan.user_id == user_id,
                WorkoutPlan.id == workout_plan_id,
            )
            .options(selectinload(ExercisePlan.exercise_set_plans))
        )
        ExercisePlanBase.update_entity(payload, entity=exercise_plan)
        
        await self.repos.session.commit()

        return await self.repos.exercise_plan.get_one(
            val=exercise_plan_id,
            options=[selectinload(ExercisePlan.exercise_set_plans)],
        )

    async def get_one_exercise_plan(
        self, workout_plan_id: int, user_id: int, exercise_plan_id: int
    ) -> ExercisePlanBase:
        return await self.repos.exercise_plan.find_one_exercise_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
        )

    @validate_order_in_plan_number
    async def add_exercise_plan_to_workout(
        self, workout_plan_id: int, payload: ExercisePlanBase, **kwargs
    ):
        payload.workout_plan_id = workout_plan_id
        created_plan = ExercisePlanBase.create_entity(payload)
        self.repos.session.add(created_plan)
        await self.repos.session.commit()
        return await self.repos.exercise_plan.get_one(
            val=created_plan.id, options=[selectinload(ExercisePlan.exercise_set_plans)]
        )

    async def delete_exercise_plan(
        self, workout_plan_id: int, user_id: int, exercise_plan_id: int
    ):
        deleted_exercise = await self.repos.exercise_plan.delete_exercise_plan(
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            user_id=user_id,
        )
        session = self.repos.session
        old_order = deleted_exercise.order_in_plan
        # Shift remaining items down (decrement order_in_plan by 1)
        # This fills the gap left by the deleted exercise.
        await session.execute(
            update(ExercisePlan)
            .where(
                ExercisePlan.workout_plan_id == workout_plan_id,
                ExercisePlan.order_in_plan > old_order,
            )
            .values(order_in_plan=ExercisePlan.order_in_plan - 1)
        )

        return deleted_exercise
