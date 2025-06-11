from app.api.v1.workouts.schema import ExerciseSetPlanBase
from app.core.database.base_repo import BaseRepo
from app.models import WorkoutExerciseSetPlan


class ExerciseSetPlanRepository(BaseRepo[WorkoutExerciseSetPlan, ExerciseSetPlanBase]):
    __dbmodel__ = WorkoutExerciseSetPlan
    __model__ = ExerciseSetPlanBase

    async def create_exercise_plan(
        self, exercise_plan_id: int, exercise_set_plan: ExerciseSetPlanBase, commit: bool = True
    ):
        exercise_set_plan_data = ExerciseSetPlanBase(
            workout_exercise_plan_id=exercise_plan_id,
            set_number=exercise_set_plan.set_number,
            target_reps=exercise_set_plan.target_reps,
            target_weight=exercise_set_plan.target_weight,
            target_duration_seconds=exercise_set_plan.target_duration_seconds,
        )

        created_exercise_set_plan = await self.create(
            data=exercise_set_plan_data, commit=commit
        )

        return created_exercise_set_plan

    async def create_many_exercise_set_plans(
        self,
        exercise_plan_id: int,
        exercise_set_plans: list[ExerciseSetPlanBase],
        commit: bool = True,
    ):
        def mapper(exercise_set_plan: ExerciseSetPlanBase):
            return ExerciseSetPlanBase(
                set_number=exercise_set_plan.set_number,
                target_reps=exercise_set_plan.target_reps,
                target_weight=exercise_set_plan.target_weight,
                target_duration_seconds=exercise_set_plan.target_duration_seconds,
                workout_exercise_plan_id=exercise_plan_id,
            )

        exercise_set_plans = list(map(mapper, exercise_set_plans))

        created_exercise_set_plans = await self.create_many(
            data=exercise_set_plans, commit=commit
        )
        return created_exercise_set_plans
