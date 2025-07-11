

from app.api.v1.categories.schema import ExerciseByCategoryResponse
from app.models import Exercise, ExerciseCategory
from app.repositories import Repos


class CategoryService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_all_categories(self):
        return await self.repos.category.get_all()

    async def get_one_category(self, category_id: int):
        return await self.repos.category.get_one(val=category_id)

    async def get_exercises_by_category(self, category_id: int):
        return await self.repos.exercise.get_all(
            where_clause=[
                ExerciseCategory.category_id == category_id,
                ExerciseCategory.exercise_id == Exercise.id
            ],
            return_model=ExerciseByCategoryResponse
        )
