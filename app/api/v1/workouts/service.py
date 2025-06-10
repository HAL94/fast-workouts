from app.repositories import WorkoutPlanRepository
from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    WorkoutPlanBase,
    WorkoutPlanRead,
)
from app.core.auth.schema import UserRead
from app.models import WorkoutPlan


class WorkoutPlanService:
    def __init__(self, workout_repo: WorkoutPlanRepository):
        self.workout_repo = workout_repo

    async def get_workouts(self, user_data: UserRead) -> list[WorkoutPlanRead]:
        # endpoint should also be paginated
        workout_pagination = await self.workout_repo.get_many(
            page=1,
            size=5,
            where_clause=[WorkoutPlan.user_id == user_data.id],
        )

        workout_plans: list[WorkoutPlanRead] = []

        for item in workout_pagination.result:
            exercise_count = await self.workout_repo.get_exercise_count_for_workout(
                item.id
            )
            target_workout_plan_muscles = (
                await self.workout_repo.get_muscles_for_workout(item.id)
            )
            item_result = WorkoutPlanRead(
                id=item.id,
                title=item.title,
                user_id=item.user_id,
                comments=item.comments,
                description=item.description,
                exercises_count=exercise_count,
                muscle_groups=target_workout_plan_muscles,
            )
            workout_plans.append(item_result)

        workout_pagination.result = workout_plans

        return workout_pagination

    async def create_workout_plan(
        self, user_data: UserRead, data: CreateWorkoutPlanRequest
    ) -> WorkoutPlanBase:
        result = await self.workout_repo.create_workout_plan(
            user_id=user_data.id,
            workout_data=data,
        )

        return result
