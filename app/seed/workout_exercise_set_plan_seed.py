from typing import Any
from app.models import WorkoutExerciseSetPlan
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_exercise_set_plans_data


class WorkoutExerciseSetPlanSeed(BaseSeed):
    __model__ = WorkoutExerciseSetPlan

    def create_workout_exercise_set_plan(
        self, data: dict[str, Any]
    ) -> WorkoutExerciseSetPlan:
        return self.create_one(data)

    def create_many(self) -> list[WorkoutExerciseSetPlan]:
        records = []
        for item in workout_exercise_set_plans_data:
            created_record = self.create_workout_exercise_set_plan(item)
            if created_record is not None:
                records.append(created_record)

        self.session.commit()
        self.data = records
        self.seeded = True
        return records
