

# --- Paginated Read Schema ---
# Represents pagination schema for exercise resource
from typing import ClassVar
from app.api.v1.schema.category import CategoryBase
from app.api.v1.schema.exercise import ExerciseBase, MuscleGroupBase
from app.core.common.pagination_factory import PaginationFactory
from app.models import Exercise

# --- Read Paginatged Schema ---
# Represents a paginated read schema for exercise resource
exercise_cols = Exercise.columns()
ExerciseListPagination = PaginationFactory.create_pagination(Exercise,
sortable_fields=exercise_cols, filterable_fields=exercise_cols
)


class ExerciseListReadPagination(ExerciseListPagination):
    pass

# --- Read Schema ---
# Represents read schema for exercise resource


class ExerciseByMuscleResponse(ExerciseBase):
    muscle_groups: ClassVar[list[MuscleGroupBase]]  # excluded


class ExerciseByCategoryResponse(ExerciseBase):
    categories: ClassVar[list[CategoryBase]]  # excluded
