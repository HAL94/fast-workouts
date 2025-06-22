from sqlalchemy.orm import selectinload
from app.core.database.base_repo import PaginatedResponse
from app.repositories import WorkoutPlanRepository
from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest,
    WorkoutPlanBase,
    WorkoutPlanReadPaginatedItem,
)
from app.core.auth.schema import UserRead
from app.models import WorkoutExercisePlan, WorkoutPlan

class WorkoutPlanService:
    def __init__(self, workout_repo: WorkoutPlanRepository):
        self.workout_repo = workout_repo

    async def get_workouts(
        self, user_data: UserRead
    ) -> PaginatedResponse[WorkoutPlanReadPaginatedItem]:
        # endpoint should also be paginated
        workout_pagination = await self.workout_repo.get_many(
            page=1,
            size=5,
            where_clause=[WorkoutPlan.user_id == user_data.id],
        )

        workout_plans: list[WorkoutPlanReadPaginatedItem] = []

        for item in workout_pagination.result:
            exercise_count = await self.workout_repo.get_exercise_count_for_workout(
                item.id
            )
            target_workout_plan_muscles = (
                await self.workout_repo.get_muscles_for_workout(item.id)
            )
            item_result = WorkoutPlanReadPaginatedItem(
                **item.model_dump(exclude_none=True, by_alias=False),
                exercises_count=exercise_count,
                muscle_groups=target_workout_plan_muscles,
            )
            workout_plans.append(item_result)

        workout_pagination.result = workout_plans

        return workout_pagination

    async def get_workout_plan(
        self, user_data: UserRead, workout_plan_id: int
    ) -> WorkoutPlanBase:
        workout_plan = await self.workout_repo.get_one(
            val=workout_plan_id,
            where_clause=[WorkoutPlan.user_id == user_data.id],
            relations=[
                selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
                    WorkoutExercisePlan.workout_exercise_set_plans
                )
            ],
        )

        # await self.workout_repo.get_workout_by_id(workout_id=workout_plan_id,)

        return workout_plan

    async def update_workout_plan(
        self, user_data: UserRead, data: UpdateWorkoutPlanRequest
    ) -> WorkoutPlanBase:
        return await self.workout_repo.update_workout_plan(
            user_id=user_data.id,
            workout_plan_id=data.id,
            update_data=data,
        )

    async def create_workout_plan(
        self, user_data: UserRead, data: CreateWorkoutPlanRequest
    ) -> WorkoutPlanBase:
        result = await self.workout_repo.create_workout_plan(
            user_id=user_data.id,
            workout_data=data,
        )

        return result

    async def delete_workout_plan(
        self, user_data: UserRead, workout_plan_id: int
    ) -> WorkoutPlanBase:
        result = await self.workout_repo.delete_workout_plan(
            user_id=user_data.id,
            workout_plan_id=workout_plan_id,
        )

        return result

    async def delete_exercise_plan(
        self, workout_plan_id: int, user_id: int, exercise_plan_id: int
    ):
        return await self.workout_repo.delete_workout_exercise_plan(
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            user_id=user_id,
        )

    async def delete_exercise_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ):
        return await self.workout_repo.delete_workout_exercise_set_plan(
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
            user_id=user_id,
        )
