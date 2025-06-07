from typing import Any
from app.models import WorkoutPlanSchedule
from app.seed.base_seed import BaseSeed
from app.seed.constants import workout_plan_schedules_data


class WorkoutPlanScheduleSeed(BaseSeed):
    __model__ = WorkoutPlanSchedule

    def create_workout_plan_schedule(
        self, data: dict[str, Any]
    ) -> WorkoutPlanSchedule:        
        return self.create_one(data)

    def create_many(self) -> list[WorkoutPlanSchedule]:
        records = []
        for item in workout_plan_schedules_data:
            created_record = self.create_workout_plan_schedule(item)
            if created_record is not None:
                records.append(created_record)
            
        self.session.commit()
        self.data = records
        self.seeded = True
        return records
