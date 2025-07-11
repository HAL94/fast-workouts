from app.api.v1.workouts.schema import ExerciseSetPlanBase
from app.core.database.base_repo import BaseRepo
from app.models import User, WorkoutExercisePlan, WorkoutExerciseSetPlan, WorkoutPlan


class ExerciseSetPlanRepository(BaseRepo[WorkoutExerciseSetPlan, ExerciseSetPlanBase]):
    __dbmodel__ = WorkoutExerciseSetPlan
    __model__ = ExerciseSetPlanBase

    async def find_one_exercise_set_plan(
        self,
        user_id: int,
        workout_plan_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ) -> WorkoutExerciseSetPlan:
        return await self.get_one(val=exercise_set_plan_id, where_clause=[
            WorkoutExerciseSetPlan.workout_exercise_plan_id == WorkoutExercisePlan.id,
            WorkoutPlan.id == WorkoutExercisePlan.workout_plan_id,
            WorkoutPlan.user_id == User.id,
            WorkoutExerciseSetPlan.id == exercise_set_plan_id,
            WorkoutExercisePlan.id == exercise_plan_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.user_id == user_id
        ])

    async def create_set_plan(
        self,
        exercise_plan_id: int,
        payload: ExerciseSetPlanBase,
        commit: bool = True,
    ):
        exercise_set_plan_data = ExerciseSetPlanBase(
            **payload.model_dump(exclude_unset=True, by_alias=False),
            workout_exercise_plan_id=exercise_plan_id,
        )

        created_exercise_set_plan = await self.create(
            data=exercise_set_plan_data, commit=commit
        )

        return created_exercise_set_plan

    async def create_many_exercise_set_plans(
        self,
        exercise_plan_id: int,
        payload: list[ExerciseSetPlanBase],
        commit: bool = True,
    ):
        def mapper(exercise_set_plan: ExerciseSetPlanBase):
            return ExerciseSetPlanBase(
                **exercise_set_plan.model_dump(exclude_unset=True, by_alias=False),
                workout_exercise_plan_id=exercise_plan_id,
            )

        exercise_set_plans = list(map(mapper, payload))

        created_exercise_set_plans = await self.create_many(
            data=exercise_set_plans, commit=commit
        )
        return created_exercise_set_plans

    async def delete_exercise_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ):
        return await self.delete_one(val=exercise_set_plan_id, where_clause=[
            WorkoutExerciseSetPlan.workout_exercise_plan_id == WorkoutExercisePlan.id,
            WorkoutPlan.id == WorkoutExercisePlan.workout_plan_id,
            WorkoutPlan.user_id == User.id,
            WorkoutExerciseSetPlan.id == exercise_set_plan_id,
            WorkoutExercisePlan.id == exercise_plan_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.user_id == user_id
        ])
