

from app.api.v1.schema.exercise import MuscleGroupBase
from app.core.database.base_repo import BaseRepo
from app.models import MuscleGroup


class MuscleGroupRepository(BaseRepo[MuscleGroupBase, MuscleGroup]):
    __dbmodel__ = MuscleGroup
    __model__ = MuscleGroupBase
