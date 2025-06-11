from app.api.v1.workouts.schema import ExercisePlanBase, ExercisePlanCreate
from app.core.database.base_repo import BaseRepo
from app.models import WorkoutExercisePlan


class ExercisePlanRepository(BaseRepo[WorkoutExercisePlan, ExercisePlanBase]):
    __dbmodel__ = WorkoutExercisePlan
    __model__ = ExercisePlanBase

    async def create_exercise_plan(
        self, workout_id: int, exercise_plan: ExercisePlanCreate, commit: bool = True
    ):
        data = WorkoutExercisePlan(
            exercise_id=exercise_plan.exercise_id,
            order_in_plan=exercise_plan.order_in_plan,
            target_sets=exercise_plan.target_sets,
            workout_plan_id=workout_id,
        )

        created_exercise_plan = await self.create(data=data, commit=commit)

        return created_exercise_plan

    async def create_many_exercise_plans(
        self,
        workout_id: int,
        exercise_plans: list[ExercisePlanCreate],
        commit: bool = True,
    ):
        data = []

        def mapper(exercise_plan: ExercisePlanCreate):
            return ExercisePlanBase(
                exercise_id=exercise_plan.exercise_id,
                order_in_plan=exercise_plan.order_in_plan,
                target_sets=exercise_plan.target_sets,
                workout_plan_id=workout_id,
            )

        data = list(map(mapper, exercise_plans))
        created_exercise_plans = await self.create_many(data=data, commit=commit)

        return created_exercise_plans
