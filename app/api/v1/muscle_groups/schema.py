

# --- Read Paginated Schema ---
# Represents a paginated read schema for Muscle Group resource
from typing import ClassVar
from app.api.v1.schema.exercise import ExerciseBase, MuscleGroupBase
from app.core.common.pagination_factory import PaginationFactory
from app.models import MuscleGroup


muscle_group_cols = MuscleGroup.columns()
MuscleGroupListPagination = PaginationFactory.create_pagination(
    model=MuscleGroup,
    sortable_fields=muscle_group_cols, 
    filterable_fields=muscle_group_cols,
)
class MuscleGroupListReadPagination(MuscleGroupListPagination):
    pass


# --- Read Schema ---
# Represents read schema for exercises by muscle groups
class ExerciseByMuscleResponse(ExerciseBase):
    muscle_groups: ClassVar[list[MuscleGroupBase]]  # excluded