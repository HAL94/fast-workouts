from app.core.database.base_repo import BaseRepo
from app.api.v1.schema.workout_session import ExerciseResultBase
from app.models import ExerciseResult

class ExerciseResultRepository(BaseRepo[ExerciseResultBase, ExerciseResult]):
    __dbmodel__ = ExerciseResultBase
    __model__ = ExerciseResult

