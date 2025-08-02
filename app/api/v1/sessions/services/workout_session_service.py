from app.api.v1.sessions.schema import (
    WorkoutSessionReadPagination,
    WorkoutSessionCreate,
)
from app.api.v1.schema.workout_session import (
    WorkoutSessionBase,
    ExerciseSetResultBase,
    ExerciseResultBase,
)
from app.models import (
    User,
    WorkoutSession,
    ExerciseResult,
    ExerciseSetResult,
    WorkoutSessionStatus,
    WorkoutPlan,
    ExercisePlan,
    ExerciseSetPlan,
)
from app.repositories import Repos

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
            options=base_options,
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

    async def get_workout_plan_by_session(self, session_id: int, user_id: int):
        found_session = await self.repos.workout_session.get_one(
            val=session_id,
            where_clause=[WorkoutSession.user_id == user_id],
        )
        workout_plan = await self.repos.workout_plan.get_one(
            val=found_session.workout_plan_id,
            where_clause=[WorkoutPlan.user_id == user_id],
            options=[
                selectinload(WorkoutPlan.exercise_plans).selectinload(
                    ExercisePlan.exercise_set_plans
                )
            ],
        )

        return workout_plan

    async def validate_session_results(
        self, user_id: int, session_id: int, workout_results: WorkoutSessionResultCreate
    ):
        workout_plan = await self.get_workout_plan_by_session(
            session_id=session_id, user_id=user_id
        )

        planned_exercises_map: dict[int, ExercisePlan] = {
            ex.id: ex for ex in workout_plan.exercise_plans
        }
        planned_sets_map: dict[int, dict[int, ExerciseSetPlan]] = {
            ep.id: {sp.id: sp for sp in ep.exercise_set_plans}
            for ep in workout_plan.exercise_plans
        }

        incoming_exercise_plan_ids = {
            result.exercise_plan_id
            for result in workout_results.workout_session_results
        }

        incoming_exercise_set_plan_ids = {
            exercise_set_result.exercise_set_plan_id
            for result in workout_results.workout_session_results
            for exercise_set_result in result.exercise_set_results
        }

        # check ownership of plans
        for incoming_ex_plan_id in incoming_exercise_plan_ids:
            if incoming_ex_plan_id not in planned_exercises_map:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exercise plan with ID: `{incoming_ex_plan_id}` not found or does not belong "
                    f"to workout plan ID: `{workout_plan.id}` for user ID: `{user_id}`.",
                )

        for ex_result_data in workout_results.workout_session_results:
            ex_plan_id = ex_result_data.exercise_plan_id
            for set_result_data in ex_result_data.exercise_set_results:
                incoming_set_plan_id = set_result_data.exercise_set_plan_id
                if incoming_set_plan_id not in planned_sets_map[ex_plan_id]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Exercise set plan with ID: `{set_result_data.exercise_set_plan_id}` not found or does not belong to "
                        f"exercise plan ID: `{ex_result_data.exercise_plan_id}` within workout plan ID: `{workout_plan.id}`.",
                    )

        existing_ex_results = await self.repos.exercise_result.get_all(
            where_clause=[
                ExerciseResult.exercise_plan_id.in_(list(incoming_exercise_plan_ids))
            ]
        )

        # Consider skipping incoming records with these ids to effectively make this API from `create` to `create or update`
        if len(existing_ex_results) != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Exercise results exist for these plans: {[ex_result.exercise_plan_id for ex_result in existing_ex_results]} "
                f"Use update API to modify.",
            )

        existing_ex_set_results = await self.repos.exercise_set_result.get_all(
            where_clause=[
                ExerciseSetResult.exercise_set_plan_id.in_(
                    incoming_exercise_set_plan_ids
                )
            ]
        )

        if len(existing_ex_set_results) != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Exercise set results exist for these set plans: {[ex_set_result.exercise_set_plan_id for ex_set_result in existing_ex_set_results]} "
                f"Use update API to modify.",
            )

        # await self.validate_exercise_plans_results(
        #     user_id=user_id,
        #     session_id=session_id,
        #     exercise_results=workout_results.workout_session_results,
        # )

        # for result_set in workout_results.workout_session_results:
        #     await self.validate_exercise_set_results(
        #         user_id=user_id,
        #         session_id=session_id,
        #         exercise_plan_id=result_set.exercise_plan_id,
        #         exercise_set_results=result_set.exercise_set_results,
        #     )

    async def create_session_results(
        self, user_id: int, session_id: int, workout_results: WorkoutSessionResultCreate
    ):
        await self.validate_session_results(
            user_id=user_id, session_id=session_id, workout_results=workout_results
        )
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
