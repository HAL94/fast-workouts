

# --- Paginated Read Schema ---
# Represents pagination schema for workout session, exercise session results and exercise session set results
from app.core.common.pagination_factory import PaginationFactory
from app.models import WorkoutSession


session_cols = WorkoutSession.columns()
SessionPagination = PaginationFactory.create_pagination(
    WorkoutSession,
    sortable_fields=session_cols, filterable_fields=session_cols
)
class WorkoutSessionReadPagination(SessionPagination):
    pass
