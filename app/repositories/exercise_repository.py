from app.api.v1.schema.exercise import ExerciseBase
from app.core.database.base_repo import BaseRepo
from app.models import Exercise


class ExerciseRepository(BaseRepo[Exercise, ExerciseBase]):
    __dbmodel__ = Exercise
    __model__ = ExerciseBase