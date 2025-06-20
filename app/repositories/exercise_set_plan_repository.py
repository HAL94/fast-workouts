from sqlalchemy import select
from app.api.v1.workouts.schema import ExerciseSetPlanBase
from app.core.database.base_repo import BaseRepo
from app.models import WorkoutExercisePlan, WorkoutExerciseSetPlan, WorkoutPlan


class ExerciseSetPlanRepository(BaseRepo[WorkoutExerciseSetPlan, ExerciseSetPlanBase]):
    __dbmodel__ = WorkoutExerciseSetPlan
    __model__ = ExerciseSetPlanBase

    async def find_one_exercise_set_plan_by_user_id(
        self, user_id: int, exercise_set_plan_id: int
    ):
        session = self.session

        exercise_set_plan = await session.scalar(
            select(WorkoutExerciseSetPlan)
            .join(
                WorkoutExercisePlan,
                WorkoutExercisePlan.id
                == WorkoutExerciseSetPlan.workout_exercise_plan_id,
            )
            .join(WorkoutPlan, WorkoutPlan.id == WorkoutExercisePlan.workout_plan_id)
            .where(
                WorkoutExerciseSetPlan.id == exercise_set_plan_id,
                WorkoutPlan.user_id == user_id,
            )
        )

        if not exercise_set_plan:
            return None

        return ExerciseSetPlanBase(**exercise_set_plan.dict())

    async def create_exercise_plan(
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
