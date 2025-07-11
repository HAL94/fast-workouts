

from typing import ClassVar
from app.api.v1.schema.category import CategoryBase
from app.api.v1.schema.exercise import ExerciseBase, MuscleGroupBase


class ExerciseByCategoryResponse(ExerciseBase):
    categories: ClassVar[list[CategoryBase]]  # excluded
    muscle_groups: ClassVar[list[MuscleGroupBase]] # excluded
