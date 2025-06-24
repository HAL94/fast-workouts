

from app.api.v1.schema.workout_plan import ScheduleBase
from app.core.database.base_repo import BaseRepo
from app.models import WorkoutPlanSchedule


class WorkoutScheduleRepository(BaseRepo[WorkoutPlanSchedule, ScheduleBase]):
    __dbmodel__ = WorkoutPlanSchedule
    __model__ = ScheduleBase

    