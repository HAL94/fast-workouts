from app.api.v1.schema.workout_plan import ScheduleBase
from app.api.v1.workouts.schema import (
    CreateWorkoutScheduleRequest,
    WorkoutPlanScheduleReadPagination,
)
from app.models import WorkoutPlanSchedule
from app.repositories import Repos

class WorkoutScheduleService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def create_workout_schedule(
        self, user_id: int, workout_plan_id: int, payload: CreateWorkoutScheduleRequest
    ):
        data = ScheduleBase(
            **payload.model_dump(by_alias=False, exclude_unset=True),
            workout_plan_id=workout_plan_id,
            user_id=user_id,
        )
        return await self.repos.workout_schedule.create(data=data)

    async def get_many_workout_schedules(
        self,
        user_id: int,
        workout_plan_id: int,
        pagination: WorkoutPlanScheduleReadPagination,
    ):
        sort_by, filter_by = pagination.convert_to_model(WorkoutPlanSchedule)
        page = pagination.page
        size = pagination.size
        return await self.repos.workout_schedule.get_many(
            page=page,
            size=size,
            where_clause=[
                *filter_by,
                WorkoutPlanSchedule.workout_plan_id == workout_plan_id,
                WorkoutPlanSchedule.user_id == user_id,
            ],
            order_clause=sort_by,
        )

    async def get_workout_schedule(
        self,
        user_id: int,
        workout_plan_id: int,
        workout_plan_schedule_id: int,
    ):
        return await self.repos.workout_schedule.get_one(
            val=workout_plan_schedule_id,
            where_clause=[
                WorkoutPlanSchedule.workout_plan_id == workout_plan_id,
                WorkoutPlanSchedule.user_id == user_id,
            ],
        )
