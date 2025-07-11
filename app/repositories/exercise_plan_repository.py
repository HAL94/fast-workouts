from sqlalchemy.orm import selectinload
from app.api.v1.workouts.schema import ExercisePlanBase, ExercisePlanCreate
from app.core.database.base_repo import BaseRepo
from app.models import ExercisePlan, WorkoutPlan


class ExercisePlanRepository(BaseRepo[ExercisePlan, ExercisePlanBase]):
    __dbmodel__ = ExercisePlan
    __model__ = ExercisePlanBase

    async def find_one_exercise_plan(
        self,
        user_id: int,
        workout_plan_id: int,
        exercise_plan_id: int,
    ) -> ExercisePlanBase | ExercisePlan | None:
        exercise_plan = await self.get_one(
            val=exercise_plan_id,
            options=[selectinload(
                ExercisePlan.workout_exercise_set_plans)],
            where_clause=[
                ExercisePlan.id == exercise_plan_id,
                WorkoutPlan.id == workout_plan_id,  # implicit join with WorkoutPlan
                WorkoutPlan.user_id == user_id])
        return exercise_plan

    async def create_many_exercise_plans(
        self,
        workout_id: int,
        payload: list[ExercisePlanCreate],
        commit: bool = True,
    ):
        data = []

        def mapper(exercise_plan: ExercisePlanCreate):
            return ExercisePlanBase(
                **exercise_plan.model_dump(
                    exclude_unset=True,
                    by_alias=False,
                    exclude={"exercise_set_plans": True},
                ),
                workout_plan_id=workout_id,
            )

        data = list(map(mapper, payload))
        created_exercise_plans = await self.create_many(data=data, commit=commit)

        return created_exercise_plans

    async def delete_exercise_plan(
        self, user_id: int, workout_plan_id: int, exercise_plan_id: int
    ) -> ExercisePlanBase:
        result = await self.delete_one(
            val=exercise_plan_id,
            field='id',
            where_clause=[ExercisePlan.id == exercise_plan_id,
                          ExercisePlan.workout_plan_id == workout_plan_id,
                          WorkoutPlan.user_id == user_id]
        )
        return result
