from app.core.database.base_repo import BaseRepo
from app.api.v1.schema.workout_session import ExerciseResultBase
from app.models import ExerciseResult

class ExerciseResultRepository(BaseRepo[ExerciseResult, ExerciseResultBase]):
    __dbmodel__ = ExerciseResult
    __model__ = ExerciseResultBase

