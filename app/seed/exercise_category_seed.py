from typing import Optional
from app.models import ExerciseCategory
from app.seed.base_seed import BaseSeed


class ExerciseCategorySeed(BaseSeed):
    __model__ = ExerciseCategory

    exercise_categories = [
        "Strength Training",
        "Bodyweight Exercises",
        "Weightlifting (Free Weights)",
        "Machine Exercises",
        "Compound Exercises",
        "Isolation Exercises",
        "Core Strength",
        "Powerlifting Focus",
        "Calisthenics",
    ]

    def _create_exercise(self) -> ExerciseCategory:
        pass

    def create_many(
        self, size: Optional[int] = len(exercise_categories)
    ) -> list[ExerciseCategory]:
        records = []

        partial_list = self.exercise_categories[:size]

        for exercise_category in partial_list:
            item = self.upsert_record({"name": exercise_category}, unique_field="name")
            records.append(item)

        return records
