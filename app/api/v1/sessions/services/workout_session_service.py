from app.api.v1.sessions.schema import (
    WorkoutSessionReadPagination,
    WorkoutSessionCreate,
)
from app.api.v1.schema.workout_session import (
    WorkoutSessionBase,
)
from app.models import (
    User,
    WorkoutSession,
    ExerciseResult,
    WorkoutSessionStatus
)
from app.repositories import Repos

from datetime import datetime
from fastapi.exceptions import HTTPException
from app.api.v1.sessions.schema import (
    WorkoutSessionResultCreate,
    ExerciseResultCreate,
)
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class WorkoutSessionService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_sessions(
        self, user_id: int, pagination: WorkoutSessionReadPagination
    ):
        base_options = [
            selectinload(WorkoutSession.workout_session_results).selectinload(
                ExerciseResult.exercise_set_results
            )
        ]
        if pagination.skip:
            return await self.repos.workout_session.get_all(
                where_clause=[WorkoutSession.user_id == user_id],
                options=base_options,
            )

        return await self.repos.workout_session.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[*pagination.filter_fields, WorkoutSession.user_id == user_id],
            order_clause=pagination.sort_fields,
            relations=base_options,
        )

    async def start_session_now(self, user_id: int, payload: WorkoutSessionCreate):
        data = WorkoutSessionBase(
            user_id=user_id,
            workout_plan_id=payload.workout_plan_id,
            status=WorkoutSessionStatus.in_progress,
        )
        return await self.repos.workout_session.create(data=data)

    async def end_session_now(self, user_id: int, session_id: int):
        found_session = await self.repos.workout_session.get_one(
            val=session_id, where_clause=[WorkoutSession.user_id == user_id]
        )

        if found_session.status == WorkoutSessionStatus.completed:
            raise HTTPException(
                detail="Workout Session is already ended", status_code=409
            )

        found_session.ended_at = datetime.now()
        found_session.status = WorkoutSessionStatus.completed

        return await self.repos.workout_session.update_one(
            found_session,
            where_clause=[
                WorkoutSession.id == found_session.id,
                WorkoutSession.user_id == user_id,
            ],
        )

    async def create_session_results(
        self, user_id: int, session_id: int, workout_results: WorkoutSessionResultCreate
    ):
        found_session = await self.repos.session.scalar(
            select(WorkoutSession).where(
                WorkoutSession.user_id == user_id, WorkoutSession.id == session_id
            )
        )

        found_session.session_comments = (
            workout_results.session_comments or found_session.session_comments
        )

        exercise_results = workout_results.workout_session_results
        
        for ex_result in exercise_results:
            ex_result.workout_session_id = found_session.id
            created_exercise_result = ExerciseResultCreate.create_entity(
                schema=ex_result
            )
            self.repos.session.add(created_exercise_result)

        await self.repos.session.commit()

        return await self.repos.workout_session.get_one(
            val=session_id,
            where_clause=[WorkoutSession.user_id == User.id],
            options=[
                selectinload(WorkoutSession.workout_session_results).selectinload(
                    ExerciseResult.exercise_set_results
                )
            ],
        )
