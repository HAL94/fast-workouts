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
from sqlalchemy import select


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

    async def validate_exercise_set_results(
        self,
        user_id: int,
        session_id: int,
        exercise_plan_id: int,
        exercise_set_results: list[ExerciseSetResultBase],
    ):
        # we validate that this session and workout plan is for the corresponding user
        workout_plan = await self.get_workout_plan_by_session(
            user_id=user_id, session_id=session_id
        )

        target_exercise_set_plan_ids = [
            result.exercise_set_plan_id for result in exercise_set_results
        ]

        # these sets belong to the user
        exercise_set_plans = (
            await self.repos.session.scalars(
                select(ExerciseSetPlan).where(
                    ExerciseSetPlan.exercise_plan_id == ExercisePlan.id,
                    ExercisePlan.id == exercise_plan_id,
                    ExerciseSetPlan.id.in_(target_exercise_set_plan_ids),
                    ExercisePlan.workout_plan_id == workout_plan.id,
                )
            )
        ).all()

        print(f"Fetched exercise_set_plans: {exercise_set_plans}")
        print(f"Attempting to add results for: {target_exercise_set_plan_ids}")

        exercise_set_plans_set = {set_plan.id for set_plan in exercise_set_plans}
        target_set_plans_set = set(target_exercise_set_plan_ids)

        difference = target_set_plans_set - exercise_set_plans_set

        if len(difference) != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Some entries refer to set plans that do not exist: {difference}",
            )

        where_clause = []
        for target_set_id in target_exercise_set_plan_ids:
            where_clause.append(ExerciseSetResult.exercise_set_plan_id == target_set_id)

        # check if there are already results for those plans
        set_results_for_target_plans = await self.repos.session.scalars(
            select(ExerciseSetResult).where(*where_clause)
        )

        set_plan_results = set_results_for_target_plans.all()

        if len(set_plan_results) != 0:
            raise HTTPException(
                status_code=400,
                detail=f"You have already entered results for these plans: {[plan.exercise_set_plan_id for plan in set_plan_results]}",
            )

    async def validate_exercise_plans_results(
        self,
        session_id: int,
        user_id: int,
        exercise_results: list[ExerciseResultBase],
    ):
        exercise_plan_ids = [result.exercise_plan_id for result in exercise_results]

        # fetch the user's workout plan by current session
        workout_plan = await self.get_workout_plan_by_session(
            session_id=session_id, user_id=user_id
        )

        found_exercise_plans = await self.repos.session.scalars(
            select(ExercisePlan).where(
                ExercisePlan.id.in_(exercise_plan_ids),
                ExercisePlan.workout_plan_id == workout_plan.id,
            )
        )

        # we could skip this check with a simple equality check,
        # but it's good to show why the op failed
        exercise_plan_seq = found_exercise_plans.all()
        exercise_plan_set = {plan.id for plan in exercise_plan_seq}
        target_plans = set(exercise_plan_ids)

        difference = target_plans - exercise_plan_set

        # check if exercise plans exist for the user's workout plan
        # do not allow entry for results that may refer to arbitrary plans (workout or exercise or sets)
        # But the entry for results should refer to plans set by the user.
        if len(difference) != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Some entries refer to exercise plans that do not exist: {difference}",
            )

        # At this point we validated that the results refer to plans set for this user.
        where_clause = []
        for target_plan_id in exercise_plan_ids:
            where_clause.append(ExerciseResult.exercise_plan_id == target_plan_id)

        # check if there are already results for those plans
        exercise_results_for_target_plans = await self.repos.session.scalars(
            select(ExerciseResult).where(*where_clause)
        )

        exercise_plan_results = exercise_results_for_target_plans.all()

        if len(exercise_plan_results) != 0:
            raise HTTPException(
                status_code=400,
                detail=f"You have already entered results for these plans: {exercise_plan_ids}",
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
        await self.validate_exercise_plans_results(
            user_id=user_id,
            session_id=session_id,
            exercise_results=workout_results.workout_session_results,
        )

        for result_set in workout_results.workout_session_results:
            await self.validate_exercise_set_results(
                user_id=user_id,
                session_id=session_id,
                exercise_plan_id=result_set.exercise_plan_id,
                exercise_set_results=result_set.exercise_set_results,
            )

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
