from typing import Any
from app.models import WorkoutSessionExerciseResult
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_session_exercise_results_data


class WorkoutSessionExerciseResultsSeed(BaseSeed):
    __model__ = WorkoutSessionExerciseResult

    def create_workout_session_exercise_result(
        self, data: dict[str, Any]
    ) -> WorkoutSessionExerciseResult:
        return self.create_one(data)

    def create_many(self) -> list[WorkoutSessionExerciseResult]:
        records = []
        for item in workout_session_exercise_results_data:
            created_record = self.create_workout_session_exercise_result(item)
            if created_record is not None:
                records.append(created_record)

        self.session.commit()
        self.data = records
        self.seeded = True
        return records
