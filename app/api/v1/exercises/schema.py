

# --- Paginated Read Schema ---
# Represents pagination schema for exercise resource
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



