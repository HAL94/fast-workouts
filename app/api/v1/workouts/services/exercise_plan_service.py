from sqlalchemy import asc, select, update
from sqlalchemy.orm import selectinload
from app.api.v1.schema.workout_plan import ExercisePlanBase
from app.api.v1.workouts.schema import ExercisePlanPagination
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

    async def update_exercise_plan(
        self,
        workout_plan_id: int,
        exercise_plan_id: int,
        user_id: int,
        payload: ExercisePlanBase,
    ):
        old_exercise = await self.repos.exercise_plan.find_one_exercise_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
        )
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
        old_order = old_exercise.order_in_plan
        new_order = payload.order_in_plan

        session = self.repos.session
        # 3. Shift other items based on movement direction
        if new_order < old_order:
            # Moving item up (e.g., from order 5 to order 2)
            # Increment order_in_plan for items that were between new_order and old_order-1
            await session.execute(
                update(ExercisePlan)
                .where(
                    ExercisePlan.workout_plan_id == workout_plan_id,
                    ExercisePlan.order_in_plan >= new_order,
                    ExercisePlan.order_in_plan < old_order,
                    ExercisePlan.id
                    != exercise_plan_id,  # Exclude the target item itself
                )
                .values(order_in_plan=ExercisePlan.order_in_plan + 1)
            )
        elif new_order > old_order:  # new_order > old_order
            # Moving item down (e.g., from order 2 to order 5)
            # Decrement order_in_plan for items that were between old_order+1 and new_order
            await session.execute(
                update(ExercisePlan)
                .where(
                    ExercisePlan.workout_plan_id == workout_plan_id,
                    ExercisePlan.order_in_plan > old_order,
                    ExercisePlan.order_in_plan <= new_order,
                    ExercisePlan.id
                    != exercise_plan_id,  # Exclude the target item itself
                )
                .values(order_in_plan=ExercisePlan.order_in_plan - 1)
            )
        # print(f"Fetched exercise_plan: {exercise_plan}")
        # update full graph (exercise plan - exercise set plan)
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

    async def add_exercise_plan_to_workout(
        self, workout_plan_id: int, user_id: int, payload: ExercisePlanBase
    ):
        await self.repos.workout_plan.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        payload.workout_plan_id = workout_plan_id
        order_in_plan = payload.order_in_plan
        # Shift existing exercises to make room for the new one
        session = self.repos.session
        await session.execute(
            update(ExercisePlan)
            .where(
                ExercisePlan.workout_plan_id == workout_plan_id,
                ExercisePlan.order_in_plan >= order_in_plan,
            )
            .values(order_in_plan=ExercisePlan.order_in_plan + 1)
        )

        created_plan = ExercisePlanBase.create_entity(payload)
        self.repos.session.add(created_plan)
        await self.repos.session.commit()

        return await self.repos.exercise_plan.get_one(
            val=created_plan.id, options=[selectinload(ExercisePlan.exercise_set_plans)]
        )

        # return await self.repos.exercise_plan.create(data=payload)

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
