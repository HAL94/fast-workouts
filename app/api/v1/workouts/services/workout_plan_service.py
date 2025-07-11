from sqlalchemy.orm import selectinload
from app.core.database.base_repo import PaginatedResponse
from app.repositories import Repos
from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest,
    WorkoutPlanBase,
    WorkoutPlanReadPaginatedItem,
    WorkoutPlanReadPagination,
)
from app.core.auth.schema import UserRead
from app.models import (
    ExercisePlan,
    WorkoutPlan,
)


class WorkoutPlanService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_workouts(
        self, user_data: UserRead, pagination: WorkoutPlanReadPagination
    ) -> PaginatedResponse[WorkoutPlanReadPaginatedItem] | list[WorkoutPlanBase]:
        if pagination.skip:
            workout_ls = await self.repos.workout_plan.get_all(where_clause=[WorkoutPlan.user_id == user_data.id])
        else:
            workout_pagination = await self.repos.workout_plan.get_many(
                page=pagination.page,
                size=pagination.size,
                where_clause=[*pagination.filter_fields,
                              WorkoutPlan.user_id == user_data.id],
                order_clause=pagination.sort_fields,
            )
            workout_ls = workout_pagination.result

        workout_plans: list[WorkoutPlanReadPaginatedItem] = []

        for item in workout_ls:
            exercise_count = (
                await self.repos.workout_plan.get_exercise_count_for_workout(item.id)
            )
            target_workout_plan_muscles = (
                await self.repos.workout_plan.get_muscles_for_workout(item.id)
            )
            item_result = WorkoutPlanReadPaginatedItem(
                **item.model_dump(exclude_none=True, by_alias=False),
                exercises_count=exercise_count,
                muscle_groups=target_workout_plan_muscles,
            )
            workout_plans.append(item_result)

        if pagination.skip:
            return workout_ls
        else:
            workout_pagination.result = workout_plans
            return workout_pagination

    async def get_workout_plan(
        self, user_data: UserRead, workout_plan_id: int
    ) -> WorkoutPlanBase:
        return await self.repos.workout_plan.get_one(
            val=workout_plan_id,
            where_clause=[WorkoutPlan.user_id == user_data.id],
            relations=[
                selectinload(WorkoutPlan.exercise_plans).selectinload(
                    ExercisePlan.exercise_set_plans
                )
            ],
        )

    async def update_workout_plan(
        self, user_data: UserRead, data: UpdateWorkoutPlanRequest
    ) -> WorkoutPlanBase:
        workout_data = await self.repos.workout_plan.get_one(
            val=data.id, where_clause=[WorkoutPlan.user_id == user_data.id]
        )
        workout_plan = WorkoutPlanBase(
            title=data.title or workout_data.title,
            description=data.description or workout_data.description,
            user_id=user_data.id,
            comments=data.comments or workout_data.comments,
        )
        await self.repos.workout_plan.update_one(
            data=workout_plan,
            where_clause=[
                WorkoutPlan.id == data.id,
                WorkoutPlan.user_id == user_data.id,
            ],
            commit=False
        )

        await self.repos.exercise_plan.update_many(data.exercise_plans)

        for exercise_plan in data.exercise_plans:
            await self.repos.exercise_set_plan.update_many(
                data=exercise_plan.exercise_set_plans,
                commit=False
            )

        await self.repos.session.commit()

        fully_loaded_workout_plan = await self.repos.workout_plan.get_one(
            val=data.id,
            where_clause=[WorkoutPlan.id == data.id],
            options=[
                selectinload(WorkoutPlan.exercise_plans).selectinload(
                    ExercisePlan.exercise_set_plans
                )
            ],
        )

        return fully_loaded_workout_plan

    async def add_workout_plan(
        self, user_data: UserRead, create_data: CreateWorkoutPlanRequest
    ) -> WorkoutPlanBase:
        workout_data_create = WorkoutPlanBase(
            title=create_data.title,
            description=create_data.description,
            user_id=user_data.id,
            comments=create_data.comments,
        )

        created_workout_data = await self.repos.workout_plan.create(
            data=workout_data_create,
            commit=False
        )

        created_exercises = await self.repos.exercise_plan.create_many_exercise_plans(
            workout_id=created_workout_data.id,
            payload=create_data.exercise_plans,
            commit=False
        )

        for index, exercise_plan in enumerate(created_exercises):
            data = create_data.exercise_plans[index]

            await self.repos.exercise_set_plan.create_many_exercise_set_plans(
                exercise_plan_id=exercise_plan.id,
                payload=data.exercise_set_plans,
                commit=False
            )

        await self.repos.session.commit()

        fully_loaded_workout_plan = await self.repos.workout_plan.get_one(
            val=created_workout_data.id,
            where_clause=[WorkoutPlan.id == created_workout_data.id],
            options=[
                selectinload(WorkoutPlan.exercise_plans).selectinload(
                    ExercisePlan.exercise_set_plans
                )
            ],
        )

        return fully_loaded_workout_plan

    async def delete_workout_plan(
        self, user_data: UserRead, workout_plan_id: int
    ) -> WorkoutPlanBase:
        return await self.repos.workout_plan.delete_one(
            val=workout_plan_id,
            where_clause=[
                WorkoutPlan.id == workout_plan_id,
                WorkoutPlan.user_id == user_data.id,
            ],
        )
