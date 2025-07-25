from app.core.database.base_repo import BaseRepo
from app.api.v1.schema.workout_session import ExerciseSetResultBase
from app.models import ExerciseSetResult

class ExerciseResultSetRepository(BaseRepo[ExerciseSetResult, ExerciseSetResultBase]):
    __dbmodel__ = ExerciseSetResult
    __model__ = ExerciseSetResultBase

