from sqlalchemy import asc, update
from app.api.v1.schema import workout_plan
from app.api.v1.schema.workout_plan import ExerciseSetPlanBase
from app.api.v1.workouts.schema import ExerciseSetPlanReadPagination
from app.models import User, WorkoutExercisePlan, WorkoutExerciseSetPlan, WorkoutPlan
from app.repositories import Repos


class ExerciseSetPlanService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def add_set_to_exercise_plan(
        self,
        exercise_plan_id: int,
        workout_plan_id: int,
        user_id: int,
        payload: ExerciseSetPlanBase,
    ):
        # verify if exercise plan and workout plan belong to user
        await self.repos.exercise_plan.find_one_exercise_plan(
            workout_plan_id=workout_plan_id,
            user_id=user_id,
            exercise_plan_id=exercise_plan_id,
        )
        return await self.repos.exercise_set_plan.create_set_plan(
            exercise_plan_id=exercise_plan_id,
            payload=payload,
        )

    async def get_one_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ) -> ExerciseSetPlanBase:
        exercise_set_plan = (
            await self.repos.exercise_set_plan.find_one_exercise_set_plan(
                workout_plan_id=workout_plan_id,
                user_id=user_id,
                exercise_plan_id=exercise_plan_id,
                exercise_set_plan_id=exercise_set_plan_id,
            )
        )

        return ExerciseSetPlanBase(**exercise_set_plan.dict())

    async def get_many_set_plans(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        pagination: ExerciseSetPlanReadPagination,
    ):
        base_where_clause = [
            WorkoutExerciseSetPlan.workout_exercise_plan_id == WorkoutExercisePlan.id,
            WorkoutExercisePlan.workout_plan_id == WorkoutPlan.id,
            WorkoutPlan.user_id == User.id,
            User.id == user_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutExercisePlan.id == exercise_plan_id,
        ]
        base_order_clause = [asc(WorkoutExerciseSetPlan.set_number)]

        if pagination.skip:
            return await self.repos.exercise_set_plan.get_all(
                where_clause=base_where_clause,
                order_clause=base_order_clause)

        return await self.repos.exercise_set_plan.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[
                *pagination.filter_fields,
                *base_where_clause
            ],
            order_clause=[*pagination.sort_fields,
                          *base_order_clause],
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
        )

        session = self.repos.session
        old_set_number = deleted_set.set_number

        await session.execute(
            update(WorkoutExerciseSetPlan)
            .where(
                WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id,
                WorkoutExerciseSetPlan.set_number > old_set_number,
            )
            .values(set_number=WorkoutExerciseSetPlan.set_number - 1)
        )
        await session.commit()

        return deleted_set

    async def update_set_plan(
        self,
        exercise_set_plan_id: int,
        exercise_plan_id: int,
        workout_plan_id: int,
        user_id: int,
        payload: ExerciseSetPlanBase,
    ):
        old_set_plan = await self.repos.exercise_set_plan.find_one_exercise_set_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
        )
        new_order = payload.set_number
        old_order = old_set_plan.set_number

        session = self.repos.session
        if new_order < old_order:
            # Moving item up (e.g., from order 5 to order 2)
            # Increment order_in_plan for items that were between new_order and old_order-1
            await session.execute(
                update(WorkoutExerciseSetPlan)
                .where(
                    WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id,
                    WorkoutExerciseSetPlan.set_number >= new_order,
                    WorkoutExerciseSetPlan.set_number < old_order,
                    WorkoutExerciseSetPlan.id
                    != exercise_set_plan_id,  # Exclude the target item itself
                )
                .values(set_number=WorkoutExerciseSetPlan.set_number + 1)
            )
        elif new_order > old_order:  # new_order > old_order
            # Moving item down (e.g., from order 2 to order 5)
            # Decrement order_in_plan for items that were between old_order+1 and new_order
            await session.execute(
                update(WorkoutExerciseSetPlan)
                .where(
                    WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id,
                    WorkoutExerciseSetPlan.set_number > old_order,
                    WorkoutExerciseSetPlan.set_number <= new_order,
                    WorkoutExerciseSetPlan.id
                    != exercise_set_plan_id,  # Exclude the target item itself
                )
                .values(set_number=WorkoutExerciseSetPlan.set_number - 1)
            )
        return await self.repos.exercise_set_plan.update_one(
            data=payload,
            where_clause=[WorkoutExerciseSetPlan.id == exercise_set_plan_id],
        )
