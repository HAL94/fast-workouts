

# --- Paginated Read Schema ---
# Represents pagination schema for exercise resource
from typing import ClassVar
from app.api.v1.schema.exercise import ExerciseBase, MuscleGroupBase
from app.core.common.pagination_factory import PaginationFactory
from app.models import Exercise


exercise_cols = Exercise.columns()
ExerciseListPagination = PaginationFactory.create_pagination(
    sortable_fields=exercise_cols, filterable_fields=exercise_cols
)
class ExerciseListReadPagination(ExerciseListPagination):
    pass

# --- Read Schema ---
# Represents read schema for exercise resource
class ExerciseByMuscleResponse(ExerciseBase):
    muscle_groups: ClassVar[list[MuscleGroupBase]] # excluded