

from app.api.v1.muscle_groups.schema import MuscleGroupListReadPagination, ExerciseByMuscleResponse
from app.models import Exercise, ExerciseMuscleGroup
from app.repositories import Repos
from sqlalchemy.orm import selectinload


class MuscleGroupService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_muscle_groups_by_id(self, muscle_group_id: int):
        return await self.repos.muscle_group.get_one(
            val=muscle_group_id
        )

    async def get_many_muscle_groups(self, pagination: MuscleGroupListReadPagination):
        return await self.repos.muscle_group.get_many(
            page=pagination.page,
            size=pagination.size,
            order_clause=pagination.sort_fields,
            where_clause=pagination.filter_fields)

    async def get_exercises_by_muscle_group(self, muscle_group_id: int):
        # implicit joins
        return await self.repos.exercise.get_all(
            where_clause=[ExerciseMuscleGroup.exercise_id == Exercise.id,
                          ExerciseMuscleGroup.muscle_group_id == muscle_group_id],
            options=[selectinload(Exercise.categories)],
            return_model=ExerciseByMuscleResponse
        )
