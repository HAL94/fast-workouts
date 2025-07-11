from typing import Any
from app.models import ExerciseSetResult
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_session_exercise_set_results_data


class WorkoutSessionExerciseResultSetSeed(BaseSeed):
    __model__ = ExerciseSetResult

    def create_workout_session_exercise_set_results(
        self, data: dict[str, Any]
    ) -> ExerciseSetResult:
        return self.create_one(data)

    def create_many(self) -> list[ExerciseSetResult]:
        records = []
        for item in workout_session_exercise_set_results_data:
            created_record = self.create_workout_session_exercise_set_results(item)
            if created_record is not None:
                records.append(created_record)

        self.session.commit()
        self.data = records
        self.seeded = True
        return records
