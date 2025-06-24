from sqlalchemy import asc, update
from sqlalchemy.orm import selectinload
from app.api.v1.schema.workout_plan import (
    ExercisePlanBase,
    ExerciseSetPlanBase,
    ScheduleBase,
)
from app.core.database.base_repo import PaginatedResponse
from app.repositories import Repos
from app.api.v1.workouts.schema import (
    CreateWorkoutPlanRequest,
    CreateWorkoutScheduleRequest,
    ExercisePlanReadPagination,
    ExerciseSetPlanReadPagination,
    UpdateWorkoutPlanRequest,
    WorkoutPlanBase,
    WorkoutPlanReadPaginatedItem,
    WorkoutPlanReadPagination,
    WorkoutPlanScheduleReadPagination,
)
from app.core.auth.schema import UserRead
from app.models import (
    WorkoutExercisePlan,
    WorkoutExerciseSetPlan,
    WorkoutPlan,
    WorkoutPlanSchedule,
)


class WorkoutPlanService:
    def __init__(self, repos: Repos):
        self.repos = repos

    async def get_many_workouts(
        self, user_data: UserRead, pagination: WorkoutPlanReadPagination
    ) -> PaginatedResponse[WorkoutPlanReadPaginatedItem]:
        # endpoint should also be paginated
        sort_by, filter_by = pagination.convert_to_model(WorkoutPlan)
        workout_pagination = await self.repos.workout_plan.get_many(
            page=pagination.page,
            size=pagination.size,
            where_clause=[*filter_by, WorkoutPlan.user_id == user_data.id],
            order_clause=sort_by,
        )

        workout_plans: list[WorkoutPlanReadPaginatedItem] = []

        for item in workout_pagination.result:
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

        workout_pagination.result = workout_plans

        return workout_pagination

    async def get_workout_plan(
        self, user_data: UserRead, workout_plan_id: int
    ) -> WorkoutPlanBase:
        return await self.repos.workout_plan.get_one(
            val=workout_plan_id,
            where_clause=[WorkoutPlan.user_id == user_data.id],
            relations=[
                selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
                    WorkoutExercisePlan.workout_exercise_set_plans
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
        )

        await self.repos.exercise_plan.update_many(data.workout_exercise_plans)

        for exercise_plan in data.workout_exercise_plans:
            await self.repos.exercise_set_plan.update_many(
                data=exercise_plan.workout_exercise_set_plans,
            )

        fully_loaded_workout_plan = await self.repos.workout_plan.get_one(
            val=data.id,
            where_clause=[WorkoutPlan.id == data.id],
            relations=[
                selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
                    WorkoutExercisePlan.workout_exercise_set_plans
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
            data=workout_data_create
        )

        created_exercises = await self.repos.exercise_plan.create_many_exercise_plans(
            workout_id=created_workout_data.id,
            payload=create_data.workout_exercise_plans,
        )

        for index, exercise_set_plan in enumerate(created_exercises):
            data = create_data.workout_exercise_plans[index]

            await self.repos.exercise_set_plan.create_many_exercise_set_plans(
                exercise_plan_id=exercise_set_plan.id,
                payload=data.workout_exercise_set_plans,
            )

        fully_loaded_workout_plan = await self.repos.workout_plan.get_one(
            val=created_workout_data.id,
            where_clause=[WorkoutPlan.id == created_workout_data.id],
            relations=[
                selectinload(WorkoutPlan.workout_exercise_plans).selectinload(
                    WorkoutExercisePlan.workout_exercise_set_plans
                )
            ],
        )

        return fully_loaded_workout_plan

    async def get_many_exercise_plans(
        self,
        workout_plan_id: int,
        user_id: int,
        pagionation: ExercisePlanReadPagination,
    ):
        # verify if workout plan belongs to user
        await self.repos.workout_plan.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        sort_by, filter_by = pagionation.convert_to_model(WorkoutExercisePlan)
        return await self.repos.exercise_plan.get_many(
            page=pagionation.page,
            size=pagionation.size,
            where_clause=[
                *filter_by,
                WorkoutExercisePlan.workout_plan_id == workout_plan_id,
            ],
            order_clause=[*sort_by, asc(WorkoutExercisePlan.order_in_plan)],
        )

    async def get_exercise_plan(
        self, workout_plan_id: int, user_id: int, exercise_plan_id: int
    ) -> ExercisePlanBase:
        return await self.repos.exercise_plan.find_one_exercise_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
        )

    async def get_many_set_plans(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        pagionation: ExerciseSetPlanReadPagination,
    ):
        await self.repos.exercise_plan.find_one_exercise_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
        )
        sort_by, filter_by = pagionation.convert_to_model(WorkoutExerciseSetPlan)
        return await self.repos.exercise_set_plan.get_many(
            page=pagionation.page,
            size=pagionation.size,
            where_clause=[
                *filter_by,
                WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id,
            ],
            order_clause=[*sort_by, asc(WorkoutExerciseSetPlan.set_number)],
        )

    async def get_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ) -> ExerciseSetPlanBase:
        exercise_set_plan = (
            await self.repos.exercise_set_plan.find_one_exercise_set_plan(
                workout_plan_id=workout_plan_id,
                user_id=user_id,
                exercise_plan_id=exercise_plan_id,
                exercise_set_plan_id=exercise_set_plan_id,
            )
        )

        return ExerciseSetPlanBase(**exercise_set_plan.dict())

    async def add_exercise_plan_to_workout(
        self, workout_plan_id: int, user_id: int, payload: ExercisePlanBase
    ):
        await self.repos.workout_plan.get_one(
            val=workout_plan_id, where_clause=[WorkoutPlan.user_id == user_id]
        )
        payload.workout_plan_id = workout_plan_id
        order_in_plan = payload.order_in_plan
        # Shift existing exercises to make room for the new one
        session = self.repos.session
        await session.execute(
            update(WorkoutExercisePlan)
            .where(
                WorkoutExercisePlan.workout_plan_id == workout_plan_id,
                WorkoutExercisePlan.order_in_plan >= order_in_plan,
            )
            .values(order_in_plan=WorkoutExercisePlan.order_in_plan + 1)
        )
        return await self.repos.exercise_plan.create(data=payload)

    async def add_set_to_exercise_plan(
        self,
        exercise_plan_id: int,
        workout_plan_id: int,
        user_id: int,
        payload: ExerciseSetPlanBase,
    ):
        # verify if exercise plan and workout plan belong to user
        await self.repos.exercise_plan.find_one_exercise_plan(
            workout_plan_id=workout_plan_id,
            user_id=user_id,
            exercise_plan_id=exercise_plan_id,
        )
        return await self.repos.exercise_set_plan.create_set_plan(
            exercise_plan_id=exercise_plan_id,
            payload=payload,
        )

    async def update_set_plan(
        self,
        exercise_set_plan_id: int,
        exercise_plan_id: int,
        workout_plan_id: int,
        user_id: int,
        payload: ExerciseSetPlanBase,
    ):
        old_set_plan = await self.repos.exercise_set_plan.find_one_exercise_set_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
        )
        new_order = payload.set_number
        old_order = old_set_plan.set_number

        session = self.repos.session
        if new_order < old_order:
            # Moving item up (e.g., from order 5 to order 2)
            # Increment order_in_plan for items that were between new_order and old_order-1
            await session.execute(
                update(WorkoutExerciseSetPlan)
                .where(
                    WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id,
                    WorkoutExerciseSetPlan.set_number >= new_order,
                    WorkoutExerciseSetPlan.set_number < old_order,
                    WorkoutExerciseSetPlan.id
                    != exercise_set_plan_id,  # Exclude the target item itself
                )
                .values(set_number=WorkoutExerciseSetPlan.set_number + 1)
            )
        elif new_order > old_order:  # new_order > old_order
            # Moving item down (e.g., from order 2 to order 5)
            # Decrement order_in_plan for items that were between old_order+1 and new_order
            await session.execute(
                update(WorkoutExerciseSetPlan)
                .where(
                    WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id,
                    WorkoutExerciseSetPlan.set_number > old_order,
                    WorkoutExerciseSetPlan.set_number <= new_order,
                    WorkoutExerciseSetPlan.id
                    != exercise_set_plan_id,  # Exclude the target item itself
                )
                .values(set_number=WorkoutExerciseSetPlan.set_number - 1)
            )
        return await self.repos.exercise_set_plan.update_one(
            data=payload,
            where_clause=[WorkoutExerciseSetPlan.id == exercise_set_plan_id],
        )

    async def update_exercise_plan(
        self,
        workout_plan_id: int,
        exercise_plan_id: int,
        user_id: int,
        payload: ExercisePlanBase,
    ):
        old_exercise = await self.repos.exercise_plan.find_one_exercise_plan(
            user_id=user_id,
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            return_as_base=True,
        )
        old_order = old_exercise.order_in_plan
        new_order = payload.order_in_plan

        session = self.repos.session
        # 3. Shift other items based on movement direction
        if new_order < old_order:
            # Moving item up (e.g., from order 5 to order 2)
            # Increment order_in_plan for items that were between new_order and old_order-1
            await session.execute(
                update(WorkoutExercisePlan)
                .where(
                    WorkoutExercisePlan.workout_plan_id == workout_plan_id,
                    WorkoutExercisePlan.order_in_plan >= new_order,
                    WorkoutExercisePlan.order_in_plan < old_order,
                    WorkoutExercisePlan.id
                    != exercise_plan_id,  # Exclude the target item itself
                )
                .values(order_in_plan=WorkoutExercisePlan.order_in_plan + 1)
            )
        elif new_order > old_order:  # new_order > old_order
            # Moving item down (e.g., from order 2 to order 5)
            # Decrement order_in_plan for items that were between old_order+1 and new_order
            await session.execute(
                update(WorkoutExercisePlan)
                .where(
                    WorkoutExercisePlan.workout_plan_id == workout_plan_id,
                    WorkoutExercisePlan.order_in_plan > old_order,
                    WorkoutExercisePlan.order_in_plan <= new_order,
                    WorkoutExercisePlan.id
                    != exercise_plan_id,  # Exclude the target item itself
                )
                .values(order_in_plan=WorkoutExercisePlan.order_in_plan - 1)
            )
        return await self.repos.exercise_plan.update_one(
            data=payload,
            where_clause=[
                WorkoutExercisePlan.id == exercise_plan_id,
                WorkoutExercisePlan.workout_plan_id == workout_plan_id,
            ],
        )

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

    async def delete_exercise_plan(
        self, workout_plan_id: int, user_id: int, exercise_plan_id: int
    ):
        deleted_exercise = await self.repos.exercise_plan.delete_exercise_plan(
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            user_id=user_id,
        )
        session = self.repos.session
        old_order = deleted_exercise.order_in_plan
        # Shift remaining items down (decrement order_in_plan by 1)
        # This fills the gap left by the deleted exercise.
        await session.execute(
            update(WorkoutExercisePlan)
            .where(
                WorkoutExercisePlan.workout_plan_id == workout_plan_id,
                WorkoutExercisePlan.order_in_plan > old_order,
            )
            .values(order_in_plan=WorkoutExercisePlan.order_in_plan - 1)
        )

        return deleted_exercise

    async def delete_set_plan(
        self,
        workout_plan_id: int,
        user_id: int,
        exercise_plan_id: int,
        exercise_set_plan_id: int,
    ):
        return await self.repos.exercise_set_plan.delete_exercise_set_plan(
            workout_plan_id=workout_plan_id,
            exercise_plan_id=exercise_plan_id,
            exercise_set_plan_id=exercise_set_plan_id,
            user_id=user_id,
        )

    async def get_many_workout_schedules(
        self,
        user_id: int,
        workout_plan_id: int,
        pagination: WorkoutPlanScheduleReadPagination,
    ):
        sort_by, filter_by = pagination.convert_to_model(WorkoutPlanSchedule)
        page = pagination.page
        size = pagination.size
        return await self.repos.workout_schedule.get_many(
            page=page,
            size=size,
            where_clause=[
                *filter_by,
                WorkoutPlanSchedule.workout_plan_id == workout_plan_id,
                WorkoutPlanSchedule.user_id == user_id,
            ],
            order_clause=sort_by,
        )

    async def get_workout_schedule(
        self,
        user_id: int,
        workout_plan_id: int,
        workout_plan_schedule_id: int,
    ):
        return await self.repos.workout_schedule.get_one(
            val=workout_plan_schedule_id,
            where_clause=[
                WorkoutPlanSchedule.workout_plan_id == workout_plan_id,
                WorkoutPlanSchedule.user_id == user_id,
            ],
        )

    async def create_workout_schedule(
        self, user_id: int, workout_plan_id: int, payload: CreateWorkoutScheduleRequest
    ):      
        data = ScheduleBase(
            **payload.model_dump(by_alias=False, exclude_unset=True),
            workout_plan_id=workout_plan_id,
            user_id=user_id,
        )
        
        print(f"Data for schedule: {data}")

        return await self.repos.workout_schedule.create(data=data)
    