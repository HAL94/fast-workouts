from app.api.v1.sessions.schema import (
    WorkoutSessionReadPagination,
    WorkoutSessionCreate,
)
from app.api.v1.schema.workout_session import (
    WorkoutSessionBase,
    ExerciseSetResultBase,
    ExerciseResultBase,
)
from app.models import User, WorkoutSession, ExerciseResult
from app.repositories import Repos
from app.models import WorkoutSessionStatus
from datetime import datetime
from fastapi.exceptions import HTTPException
from app.api.v1.sessions.schema import (
    WorkoutSessionResultCreate,
    ExerciseResultCreate,
    SetResultCreate,
)
from sqlalchemy.orm import selectinload


class WorkoutSessionService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_sessions(
        self, user_id: int, pagination: WorkoutSessionReadPagination
    ):
        if pagination.skip:
            return await self.repos.workout_session.get_all(
                where_clause=[WorkoutSession.user_id == User.id, User.id == user_id]
            )

        return await self.repos.workout_session.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[
                *pagination.filter_fields,
                WorkoutSession.user_id == User.id,
                User.id == user_id,
            ],
            order_clause=pagination.sort_fields,
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
        found_session = await self.repos.workout_session.get_one(
            val=session_id,
            where_clause=[WorkoutSession.user_id == user_id],
        )

        found_session.session_comments = (
            workout_results.session_comments or found_session.session_comments
        )

        def exercise_results_mapper(
            exercise_result: ExerciseResultCreate,
        ) -> ExerciseResultBase:
            return ExerciseResultBase(
                **exercise_result.model_dump(
                    exclude_unset=True,
                    by_alias=False,
                    exclude={"exercise_set_results": True},
                ),
                workout_session_id=session_id,
            )

        mapped_session_results = list(
            map(exercise_results_mapper, workout_results.workout_session_results)
        )

        print("results", mapped_session_results)

        created_session_results = await self.repos.exercise_result.create_many(
            data=mapped_session_results, commit=False
        )

        def exercise_set_result_mapper(
            exercise_set_result: SetResultCreate, exercise_result: ExerciseResultBase
        ):
            return ExerciseSetResultBase(
                **exercise_set_result.model_dump(exclude_unset=True, by_alias=False),
                exercise_result_id=exercise_result.id,
            )

        for index, exercise_result in enumerate(created_session_results):
            data = workout_results.workout_session_results[index]

            exercise_set_results = list(
                map(
                    lambda item: exercise_set_result_mapper(
                        item, exercise_result=exercise_result
                    ),
                    data.exercise_set_results,
                )
            )

            await self.repos.exercise_set_result.create_many(
                data=exercise_set_results, commit=False
            )

        await self.repos.session.commit()

        found_session = await self.repos.workout_session.get_one(
            val=session_id,
            where_clause=[WorkoutSession.user_id == User.id],
            options=[
                selectinload(WorkoutSession.workout_session_results).selectinload(
                    ExerciseResult.exercise_set_results
                )
            ],
        )

        return found_session
