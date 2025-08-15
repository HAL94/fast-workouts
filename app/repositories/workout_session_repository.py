

from app.api.v1.schema import WorkoutSessionBase
from app.core.database.base_repo import BaseRepo
from app.models import WorkoutSession


class WorkoutSessionRepository(BaseRepo[WorkoutSession, WorkoutSessionBase]):
    __dbmodel__ = WorkoutSession
    __model__ = WorkoutSessionBase
