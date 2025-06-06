from typing import Any, Optional
from app.models import ExerciseCategory
from app.seed.base_seed import BaseSeed


class ExerciseCategorySeed(BaseSeed):
    __model__ = ExerciseCategory

    exercise_categories = [
        "Strength Training",
        "Weightlifting (Free Weights)",
        "Compound Exercises",
        "Powerlifting Focus",
        "Bodyweight Exercises",
        "Machine Exercises",
        "Isolation Exercises",
        "Core Strength",
        "Calisthenics",
    ]

    def _create_exercise_category(self, name: str) -> dict[str, Any]:
        return {"name": name}

    def create_many(
        self, size: Optional[int] = len(exercise_categories)
    ) -> list[ExerciseCategory]:
        records = []
        if self.seeded:
            return self.data

        partial_list = self.exercise_categories[:size]

        for exercise_category in partial_list:
            item = self.upsert_record(
                {"name": exercise_category}, unique_fields=["name"]
            )
            if item is not None:
                records.append(item)

        self.data = records
        self.seeded = True
        return records
