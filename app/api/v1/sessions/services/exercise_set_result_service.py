from app.dependencies.repositories import Repos
from app.api.v1.schema.workout_session import ExerciseSetResultBase
from app.api.v1.sessions.schema import ExerciseSetResultPagination

from app.models import ExerciseResult, ExerciseSetResult, WorkoutSession


class ExerciseSetResultService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def add_exercise_set_result(
        self, user_id: int, exercise_result_id: int, data: ExerciseSetResultBase
    ):
        data.exercise_result_id = exercise_result_id

        # verify the set result belong ultimatley to a user
        await self.repos.exercise_result.get_one(
            val=exercise_result_id,
            where_clause=[
                ExerciseResult.workout_session_id == WorkoutSession.id,
                WorkoutSession.user_id == user_id,
                ExerciseResult.id == exercise_result_id,
            ],
        )

        return await self.repos.exercise_set_result.create(data=data)

    async def get_many_exercise_set_results(
        self,
        user_id: int,
        exercise_result_id: int,
        pagination: ExerciseSetResultPagination,
    ):
        base_where = [
            ExerciseSetResult.exercise_result_id == ExerciseResult.id,
            ExerciseResult.workout_session_id == WorkoutSession.id,
            ExerciseResult.id == exercise_result_id,
            WorkoutSession.user_id == user_id,
        ]
        if pagination.skip:
            return await self.repos.exercise_set_result.get_all(where_clause=base_where)

        return await self.repos.exercise_set_result.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[*base_where, *pagination.filter_fields],
            order_clause=pagination.sort_fields,
        )

    async def get_one_exercise_set_result(
        self, set_result_id: int, exercise_result_id: int, user_id: int
    ):
        base_where = [
            ExerciseSetResult.exercise_result_id == ExerciseResult.id,
            ExerciseResult.workout_session_id == WorkoutSession.id,
            ExerciseResult.id == exercise_result_id,
            WorkoutSession.user_id == user_id,
        ]

        return await self.repos.exercise_set_result.get_one(
            val=set_result_id, where_clause=base_where
        )

    async def update_one_exercise_set_result(
        self,
        user_id: int,
        exercise_result_id: int,
        set_result_id: int,
        data: ExerciseSetResultBase,
    ):
        base_where = [
            ExerciseSetResult.exercise_result_id == ExerciseResult.id,
            ExerciseResult.workout_session_id == WorkoutSession.id,
            ExerciseSetResult.id == set_result_id,
            ExerciseResult.id == exercise_result_id,
            WorkoutSession.user_id == user_id,
        ]

        found_set = await self.repos.exercise_set_result.get_one(
            val=set_result_id, where_clause=base_where
        )

        dumped = data.model_dump(by_alias=False, exclude_unset=True)
        for key, value in dumped.items():
            if hasattr(found_set, key):
                if value != getattr(found_set, key):
                    setattr(found_set, key, value)

        return await self.repos.exercise_set_result.update_one(
            where_clause=base_where, data=found_set
        )

    async def delete_one_set_result(
        self, user_id: int, set_result_id: int, exercise_result_id: int
    ):
        base_where = [
            ExerciseSetResult.exercise_result_id == ExerciseResult.id,
            ExerciseResult.workout_session_id == WorkoutSession.id,
            ExerciseSetResult.id == set_result_id,
            ExerciseResult.id == exercise_result_id,
            WorkoutSession.user_id == user_id,
        ]
        return await self.repos.exercise_set_result.delete_one(
            val=set_result_id, where_clause=base_where
        )
