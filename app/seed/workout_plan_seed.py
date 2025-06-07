from typing import Any
from app.models import WorkoutPlan
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_plans_data


class WorkoutPlanSeed(BaseSeed):
    __model__ = WorkoutPlan

    def create_workout_plan(
        self, data: dict[str, Any]
    ) -> WorkoutPlan:        
        return self.create_one(data)

    def create_many(self) -> list[WorkoutPlan]:
        records = []
        for item in workout_plans_data:
            created_record = self.create_workout_plan(item)
            if created_record is not None:
                records.append(created_record)
            
        self.session.commit()
        self.data = records
        self.seeded = True
        return records
