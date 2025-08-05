from app.repositories import Repos
from app.api.v1.sessions.schema import (
    ExerciseResultPagination,
)
from app.api.v1.schema.workout_session import ExerciseResultBase
from app.models import WorkoutSession, ExerciseResult


class ExerciseResultService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def add_exercise_result(self, user_id: int, data: ExerciseResultBase):
        # validate if session exists for this user
        await self.repos.workout_session.get_one(
            val=data.workout_session_id,
            where_clause=[WorkoutSession.user_id == user_id],
        )
        return await self.repos.exercise_result.create(data=data)

    async def update_exercise_result(self, user_id: int, data: ExerciseResultBase):
        found_exercise = await self.repos.exercise_result.get_one(
            val=data.id,
            where_clause=[
                ExerciseResult.workout_session_id == WorkoutSession.id,
                ExerciseResult.workout_session_id == data.workout_session_id,
                WorkoutSession.user_id == user_id,
            ],
        )
        dumped = data.model_dump(
            by_alias=False, exclude_unset=True, exclude={"exercise_set_results": True}
        )
        for key, value in dumped.items():
            if hasattr(found_exercise, key):
                if value != getattr(found_exercise, key):
                    setattr(found_exercise, key, value)

        return await self.repos.exercise_result.update_one(
            found_exercise, where_clause=[ExerciseResult.id == found_exercise.id]
        )

    async def remove_exercise_result(self, user_id: int, exercise_result_id: int):
        return await self.repos.exercise_result.delete_one(
            val=exercise_result_id,
            where_clause=[
                ExerciseResult.workout_session_id == WorkoutSession.id,
                WorkoutSession.user_id == user_id,
            ],
        )

    async def get_one_exercise_result(self, user_id: int, exercise_result_id: int):
        return await self.repos.exercise_result.get_one(
            val=exercise_result_id,
            where_clause=[
                ExerciseResult.workout_session_id == WorkoutSession.id,
                WorkoutSession.user_id == user_id,
            ],
        )

    async def get_many_exercise_results(
        self, user_id: int, session_id: int, pagination: ExerciseResultPagination
    ):
        # ensure results belong to a workout session belonging to a user
        base_where = [
            ExerciseResult.workout_session_id == WorkoutSession.id,
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
        ]
        if pagination.skip:
            return await self.repos.exercise_result.get_all(where_clause=base_where)
        return await self.repos.exercise_result.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[*base_where, *pagination.filter_fields],
            order_clause=pagination.sort_fields,
        )
