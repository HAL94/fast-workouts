

from app.api.v1.sessions.schema import WorkoutSessionReadPagination
from app.models import User, WorkoutSession
from app.repositories import Repos


class WorkoutSessionService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_sessions(self, user_id: int, pagination: WorkoutSessionReadPagination):
        if pagination.skip:
            return await self.repos.workout_session.get_all(where_clause=[WorkoutSession.user_id == User.id,
                                                                          User.id == user_id])

        return await self.repos.workout_session.get_many(page=pagination.page, size=pagination.size,
                                                         where_clause=[
                                                             *pagination.filter_fields,
                                                             WorkoutSession.user_id == User.id,
                                                             User.id == user_id],
                                                         order_clause=pagination.sort_fields)
