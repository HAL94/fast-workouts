from typing import Any
from app.models import WorkoutSession
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_sessions_data


class WorkoutSessionSeed(BaseSeed):
    __model__ = WorkoutSession

    def create_workout_session(
        self, data: dict[str, Any]
    ) -> WorkoutSession:        
        return self.create_one(data)

    def create_many(self) -> list[WorkoutSession]:
        records = []
        for item in workout_sessions_data:
            created_record = self.create_workout_session(item)
            if created_record is not None:
                records.append(created_record)
            
        self.session.commit()
        self.data = records
        self.seeded = True
        return records
