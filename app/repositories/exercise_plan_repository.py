from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.v1.workouts.schema import ExercisePlanBase, ExercisePlanCreate
from app.core.database.base_repo import BaseRepo
from app.models import WorkoutExercisePlan, WorkoutPlan


class ExercisePlanRepository(BaseRepo[WorkoutExercisePlan, ExercisePlanBase]):
    __dbmodel__ = WorkoutExercisePlan
    __model__ = ExercisePlanBase

    async def find_one_exercise_plan_by_user_id(
        self,
        user_id: int,
        workout_plan_id: int,
        exercise_plan_id: int,
        return_as_base: bool = False,
    ) -> ExercisePlanBase | WorkoutExercisePlan | None:
        session = self.session

        exercise_plan = await session.scalar(
            select(WorkoutExercisePlan)
            .options(selectinload(WorkoutExercisePlan.workout_exercise_set_plans))
            .join(WorkoutPlan, WorkoutPlan.id == WorkoutExercisePlan.workout_plan_id)
            .where(
                WorkoutExercisePlan.id == exercise_plan_id,
                WorkoutPlan.id == workout_plan_id,
                WorkoutPlan.user_id == user_id,
            )
        )

        if not exercise_plan:
            return None

        if return_as_base:
            return exercise_plan

        return ExercisePlanBase(**exercise_plan.dict())

    async def create_exercise_plan(
        self, workout_id: int, payload: ExercisePlanCreate, commit: bool = True
    ):
        data = WorkoutExercisePlan(
            **payload.model_dump(
                exclude_unset=True, by_alias=False, exclude={"workout_plan_id": True}
            ),
            workout_plan_id=workout_id,
        )

        created_exercise_plan = await self.create(data=data, commit=commit)

        return created_exercise_plan

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
                    exclude={"workout_exercise_set_plans": True},
                ),
                workout_plan_id=workout_id,
            )

        data = list(map(mapper, payload))
        created_exercise_plans = await self.create_many(data=data, commit=commit)

        return created_exercise_plans

    async def delete_exercise_plan(
        self, user_id: int, workout_plan_id: int, exercise_plan_id: int
    ) -> ExercisePlanBase:
        result: WorkoutExercisePlan = await self.find_one_exercise_plan_by_user_id(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            return_as_base=True,
        )
        await self.session.delete(result)
        await self.session.commit()

        return ExercisePlanBase(**result.dict())
