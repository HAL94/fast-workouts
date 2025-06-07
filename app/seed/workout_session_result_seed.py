from typing import Any
from app.models import WorkoutSessionResult
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_session_results_data


class WorkoutSessionResultSeed(BaseSeed):
    __model__ = WorkoutSessionResult

    def create_workout_session_result(
        self, data: dict[str, Any]
    ) -> WorkoutSessionResult:        
        return self.create_one(data)

    def create_many(self) -> list[WorkoutSessionResult]:
        records = []
        for item in workout_session_results_data:
            created_record = self.create_workout_session_result(item)
            if created_record is not None:
                records.append(created_record)
            
        self.session.commit()
        self.data = records
        self.seeded = True
        return records
