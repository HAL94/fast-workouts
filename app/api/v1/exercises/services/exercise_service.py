
from app.api.v1.exercises.schema import ExerciseListReadPagination
from app.models import Exercise
from app.repositories import Repos

from sqlalchemy.orm import selectinload


class ExerciseService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_exercises(self, pagination: ExerciseListReadPagination):
        sort_by, filter_by = pagination.convert_to_model(Exercise)
        return await self.repos.exercise.get_many(
            page=pagination.page, size=pagination.size,
            order_clause=sort_by, where_clause=filter_by,
            relations=[selectinload(Exercise.categories), selectinload(Exercise.muscle_groups)])

    async def get_exercies_by_muscle(self, muscle_group_id: int):
        result = await self.repos.exercise.\
            get_exercies_by_muscle(muscle_group_id=muscle_group_id)
        return result
