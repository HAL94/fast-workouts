from typing import Any
from app.models import ExercisePlan
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_exercise_plans_data


class WorkoutExercisePlanSeed(BaseSeed):
    __model__ = ExercisePlan

    def create_workout_exercise_plan(
        self, data: dict[str, Any]
    ) -> ExercisePlan:
        return self.create_one(data)

    def create_many(self) -> list[ExercisePlan]:
        records = []
        for item in workout_exercise_plans_data:
            created_record = self.create_workout_exercise_plan(item)
            if created_record is not None:
                records.append(created_record)
            
        self.session.commit()
        self.data = records
        self.seeded = True
        return records
