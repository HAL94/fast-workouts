from typing import Any
from app.models import WorkoutExercisePlan
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_exercise_plans_data


class WorkoutExercisePlanSeed(BaseSeed):
    __model__ = WorkoutExercisePlan

    def create_workout_exercise_plan(
        self, data: dict[str, Any]
    ) -> WorkoutExercisePlan:        
        return self.create_one(data)

    def create_many(self) -> list[WorkoutExercisePlan]:
        records = []
        for item in workout_exercise_plans_data:
            created_record = self.create_workout_exercise_plan(item)
            if created_record is not None:
                records.append(created_record)
            
        self.session.commit()
        self.data = records
        self.seeded = True
        return records
