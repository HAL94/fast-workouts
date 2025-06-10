from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    ExercisePlanBase,
    ExerciseSetPlanBase,
    WorkoutPlanBase,
)
from app.core.database.base_repo import BaseRepo
from app.models import (
    ExerciseMuscleGroup,
    MuscleGroup,
    WorkoutExercisePlan,
    WorkoutExerciseSetPlan,
    WorkoutPlan,
)


class WorkoutPlanRepository(BaseRepo[WorkoutPlan, WorkoutPlanBase]):
    __dbmodel__ = WorkoutPlan
    __model__ = WorkoutPlanBase

    async def get_muscles_for_workout(self, workout_id: int) -> list[str]:
        muscles_for_plan = await self.session.scalars(
            select(MuscleGroup.muscle_target)
            .join(
                ExerciseMuscleGroup,
                ExerciseMuscleGroup.muscle_group_id == MuscleGroup.id,
            )
            .join(
                WorkoutExercisePlan,
                ExerciseMuscleGroup.exercise_id == WorkoutExercisePlan.exercise_id,
            )
            .where(WorkoutExercisePlan.workout_plan_id == workout_id)
            .group_by(MuscleGroup.muscle_target)
        )

        return muscles_for_plan.all()

    async def create_workout_plan(
        self, user_id: int, workout_data: CreateWorkoutPlanRequest
    ) -> WorkoutExercisePlan:
        session = self.session

        workout_data_created = WorkoutPlan(
            title=workout_data.title,
            description=workout_data.description,
            user_id=user_id,
            comments=workout_data.comments,
        )

        for exercise_plan in workout_data.workout_exercise_plans:
            data = WorkoutExercisePlan(
                exercise_id=exercise_plan.exercise_id,
                order_in_plan=exercise_plan.order_in_plan,
                target_sets=exercise_plan.target_sets,
                workout_plan_id=workout_data_created.id,
            )
            # session.add(data)

            for exercise_set_plan in exercise_plan.workout_exercise_set_plans:
                exercise_set_plan_data = WorkoutExerciseSetPlan(
                    set_number=exercise_set_plan.set_number,
                    target_reps=exercise_set_plan.target_reps,
                    target_weight=exercise_set_plan.target_weight,
                    target_duration_seconds=exercise_set_plan.target_duration_seconds,
                )
                data.workout_exercise_set_plans.append(exercise_set_plan_data)

            workout_data_created.workout_exercise_plans.append(data)

        session.add(workout_data_created)
        await session.commit()
        await session.refresh(
            workout_data_created
        )  # Refresh the instance to get the generated ID

        # workout_plan_cursor = await session.scalars(
        #     select(WorkoutPlan)
        #     .where(WorkoutPlan.id == workout_data_created.id)
        #     .options(
        #         selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
        #             WorkoutExercisePlan.workout_exercise_set_plans
        #         )
        #     )
        # )

        # fully_loaded_workout_plan = workout_plan_cursor.unique().first()
        # print(f"workout_plan: {fully_loaded_workout_plan}")
        # print("Exercises", fully_loaded_workout_plan.workout_exercise_plans)
        # print(
        #     "First Set Plan",
        #     fully_loaded_workout_plan.workout_exercise_plans[
        #         0
        #     ].workout_exercise_set_plans,
        # )
        # created_workout_data = WorkoutPlanBase(
        #     **fully_loaded_workout_plan.dict(),
        #     workout_exercise_plans=fully_loaded_workout_plan.workout_exercise_plans,
        # )

        workout_exercise_cursor = await session.scalars(
            select(WorkoutExercisePlan)
            .where(WorkoutExercisePlan.workout_plan_id == workout_data_created.id)
            .options(selectinload(WorkoutExercisePlan.workout_exercise_set_plans))
        )

        exercise_plans = []
        for item in workout_exercise_cursor.all():
            item_transformed = ExercisePlanBase(**item.dict())
            exercise_set_plans = []
            for set_plans_item in item.workout_exercise_set_plans:
                exercise_set_plans.append(ExerciseSetPlanBase(**set_plans_item.dict()))
            item_transformed.workout_exercise_set_plans = exercise_set_plans
            exercise_plans.append(item_transformed)

        created_workout_data = WorkoutPlanBase(
            **workout_data_created.dict(), workout_exercise_plans=exercise_plans
        )
        return created_workout_data

    async def get_exercise_count_for_workout(self, workout_id: int) -> int:
        exercises_count_stmt = select(func.count()).select_from(
            select(WorkoutExercisePlan)
            .where(WorkoutExercisePlan.workout_plan_id == workout_id)
            .subquery()
        )

        return await self.session.scalar(exercises_count_stmt)
