

# --- Read Paginated Schema ---
# Represents a paginated read schema for Muscle Group resource
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