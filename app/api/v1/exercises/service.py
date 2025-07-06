
from app.api.v1.exercises.schema import ExerciseListReadPagination
from app.models import Exercise
from app.repositories import Repos

from sqlalchemy.orm import selectinload


class ExerciseService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_exercises(self, pagination: ExerciseListReadPagination):
        return await self.repos.exercise.get_many(
            page=pagination.page, size=pagination.size,
            order_clause=pagination.sort_fields, where_clause=pagination.filter_fields,
            relations=[selectinload(Exercise.categories), selectinload(Exercise.muscle_groups)])

    async def get_one_exercise(self, exercise_id: int):
        return await self.repos.exercise.get_one(val=exercise_id, options=[selectinload(Exercise.categories), selectinload(Exercise.muscle_groups)])
