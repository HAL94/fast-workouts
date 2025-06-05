from typing import Optional

from app.models import Exercise, ExerciseCategory
from app.seed.base_seed import BaseSeed
from app.seed.exercise_category_seed import ExerciseCategorySeed


class ExerciseSeed(BaseSeed):
    __model__ = Exercise

    def __init__(self, session, category_seeder: ExerciseCategorySeed):
        self.category_seeder = category_seeder
        super().__init__(session=session)
        

    def _create_exercise(self, exercise_name: str, category: ExerciseCategory) -> dict:
        return {
            "name": exercise_name,
            "description": "details",
            "exercise_category_id": category.id,
        }

    exercises_by_categories = {
        "Strength Training": [
            "Bench Press",
            "Bent-Over Row",
            "Bicep Curl",
            "Calf Raises",
            "Crunches/Sit-ups",
            "Deadlift",
            "Dumbbell Row",
            "Face Pulls",
            "Front Raise",
            "Glute Bridge/Hip Thrust",
            "Good Mornings",
            "Leg Curl",
            "Leg Extension",
            "Leg Press",
            "Lunges",
            "Overhead Press (Shoulder Press)",
            "Plank",
            "Pull-up/Chin-up",
            "Rear Delt Fly",
            "Russian Twists",
            "Shrugs",
            "Squat",
            "Tricep Extension",
        ],
        "Weightlifting (Free Weights)": [
            "Bench Press",
            "Bent-Over Row",
            "Bicep Curl",
            "Calf Raises",
            "Deadlift",
            "Dumbbell Row",
            "Face Pulls",
            "Front Raise",
            "Glute Bridge/Hip Thrust",
            "Good Mornings",
            "Lunges",
            "Overhead Press (Shoulder Press)",
            "Rear Delt Fly",
            "Shrugs",
            "Squat",
            "Tricep Extension",
            "Lateral Raise",
        ],
        "Compound Exercises": [
            "Bench Press",
            "Bent-Over Row",
            "Deadlift",
            "Dumbbell Row",
            "Face Pulls",
            "Glute Bridge/Hip Thrust",
            "Good Mornings",
            "Leg Press",
            "Lunges",
            "Overhead Press (Shoulder Press)",
            "Pull-up/Chin-up",
            "Squat",
        ],
        "Powerlifting Focus": ["Bench Press", "Deadlift", "Squat"],
        "Bodyweight Exercises": [
            "Calf Raises",
            "Crunches/Sit-ups",
            "Glute Bridge/Hip Thrust",
            "Lunges",
            "Plank",
            "Pull-up/Chin-up",
            "Russian Twists",
        ],
        "Machine Exercises": ["Leg Curl", "Leg Extension", "Leg Press"],
        "Isolation Exercises": [
            "Bicep Curl",
            "Calf Raises",
            "Glute Bridge/Hip Thrust",
            "Leg Curl",
            "Leg Extension",
            "Lateral Raise",
            "Front Raise",
            "Rear Delt Fly",
            "Shrugs",
            "Tricep Extension",
        ],
        "Core Strength": ["Crunches/Sit-ups", "Plank", "Russian Twists"],
        "Calisthenics": ["Crunches/Sit-ups", "Plank", "Pull-up/Chin-up"],
    }

    def create_many(
        self, size: Optional[int] = len(exercises_by_categories.keys())
    ) -> list[Exercise]:
        records = []
        categories = self.category_seeder.create_many()
        for cat in categories:
            exercises = self.exercises_by_categories[cat.name]
            for exercise in exercises:
                exercise_data = self._create_exercise(
                    exercise_name=exercise, category=cat
                )
                exercise_record = self.upsert_record(
                    data=exercise_data, unique_fields=["name"]
                )
                if exercise_record is not None:
                    records.append(exercise_record)
        self.data = records
        return records
