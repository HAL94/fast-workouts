# --- The Decorator ---
import functools
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional
from fastapi import HTTPException
from sqlalchemy import select, func as sqlfunc, update

from app.api.v1.schema.workout_plan import ExercisePlanBase, ExerciseSetPlanBase
from app.models import ExercisePlan, ExerciseSetPlan, WorkoutPlan

if TYPE_CHECKING:
    from app.api.v1.workouts.services.set_plan_service import ExerciseSetPlanService
    from app.api.v1.workouts.services.exercise_plan_service import ExercisePlanService


def validate_order_in_plan_number(func: Callable) -> Coroutine[Any, Any, Any]:
    """
    A decorator to validate user ownership of an workout plan and the
    validity of the order number before adding a new exercise plan.
    """

    @functools.wraps(func)
    async def wrapper(
        self: "ExercisePlanService",
        *args,
        **kwargs,
    ):
        workout_plan_id: int = kwargs.get("workout_plan_id")
        user_id: int = kwargs.get("user_id")
        payload: ExercisePlanBase = kwargs.get("payload")
        exercise_plan_id: Optional[int] = kwargs.get("exercise_plan_id")
        old_exercise: ExercisePlanBase | None = None

        # 1. validate current data belongs to user
        if exercise_plan_id:
            # 1.a get previous exercise if updating
            old_exercise = await self.repos.exercise_plan.find_one_exercise_plan(
                user_id=user_id,
                workout_plan_id=workout_plan_id,
                exercise_plan_id=exercise_plan_id,
            )
        else:
            # 1.b Else; we are adding, verify if workout plan belongs to the user.
            await self.repos.workout_plan.get_one(
                val=workout_plan_id,
                where_clause=[WorkoutPlan.user_id == user_id],
            )

        # 2. Get the current maximum order in plan order.
        max_order_in_plan = await self.repos.session.scalar(
            select(sqlfunc.max(ExercisePlan.order_in_plan)).where(
                ExercisePlan.workout_plan_id == workout_plan_id
            )
        )

        new_order = payload.order_in_plan
        # 3.a Update Scenario: we are updating an existing exercise plan
        if old_exercise and new_order > max_order_in_plan:
            raise HTTPException(
                status_code=400,
                detail=f"order_in_plan passed {payload.order_in_plan} is not valid, "
                f"order_in_plan should not exceed {max_order_in_plan}.",
            )

        # 3.b Create Scenario: validate the new order_in_plan number.
        if max_order_in_plan and new_order > (max_order_in_plan + 1):
            raise HTTPException(
                status_code=400,
                detail=f"order_in_plan passed {payload.order_in_plan} is not valid, "
                f"the next available sequence is {max_order_in_plan + 1} for updates",
            )

        # 3.c First time adding an exercise, make sure the order_in_plan = 1;
        if not max_order_in_plan and payload.order_in_plan > 1:
            raise HTTPException(
                status_code=400,
                detail=f"order_in_plan passed {payload.order_in_plan} is larger than 1",
            )

        session = self.repos.session
        if old_exercise:
            old_order = old_exercise.order_in_plan
            if new_order < old_order:
                # Moving item up (e.g., from order 5 to order 2)
                # Increment order_in_plan for items that were between new_order and old_order-1
                await session.execute(
                    update(ExercisePlan)
                    .where(
                        ExercisePlan.workout_plan_id == workout_plan_id,
                        ExercisePlan.order_in_plan >= new_order,
                        ExercisePlan.order_in_plan < old_order,
                        ExercisePlan.id
                        != exercise_plan_id,  # Exclude the target item itself
                    )
                    .values(order_in_plan=ExercisePlan.order_in_plan + 1)
                )
            elif new_order > old_order:  # new_order > old_order
                # Moving item down (e.g., from order 2 to order 5)
                # Decrement order_in_plan for items that were between old_order+1 and new_order
                await session.execute(
                    update(ExercisePlan)
                    .where(
                        ExercisePlan.workout_plan_id == workout_plan_id,
                        ExercisePlan.order_in_plan > old_order,
                        ExercisePlan.order_in_plan <= new_order,
                        ExercisePlan.id
                        != exercise_plan_id,  # Exclude the target item itself
                    )
                    .values(order_in_plan=ExercisePlan.order_in_plan - 1)
                )
        else:
            await session.execute(
                update(ExercisePlan)
                .where(
                    ExercisePlan.workout_plan_id == workout_plan_id,
                    ExercisePlan.order_in_plan >= new_order,
                )
                .values(order_in_plan=ExercisePlan.order_in_plan + 1)
            )
        return await func(
            self,
            *args,
            **kwargs,
        )

    return wrapper


def validate_set_number(func: Callable) -> Coroutine[Any, Any, Any]:
    """
    A decorator to validate user ownership of an exercise plan and the
    validity of the set number before adding a new set plan.
    """

    @functools.wraps(func)
    async def wrapper(
        self: "ExerciseSetPlanService",
        *args,
        **kwargs,
    ):
        old_set_plan: ExerciseSetPlanBase | None = None
        # 1. Verify if plan belong to the user.
        exercise_set_plan_id: int = kwargs.get("exercise_set_plan_id")
        exercise_plan_id: int = kwargs.get("exercise_plan_id")
        workout_plan_id: int = kwargs.get("workout_plan_id")
        user_id: int = kwargs.get("user_id")
        payload: ExerciseSetPlanBase = kwargs.get("payload")

        if exercise_set_plan_id:
            # 1.a updating a currently existing set plan
            old_set_plan = (
                await self.repos.exercise_set_plan.find_one_exercise_set_plan(
                    user_id=user_id,
                    workout_plan_id=workout_plan_id,
                    exercise_plan_id=exercise_plan_id,
                    exercise_set_plan_id=exercise_set_plan_id,
                )
            )
        else:
            # 1.b Else; we are adding, verify if it belongs to user
            await self.repos.exercise_plan.find_one_exercise_plan(
                workout_plan_id=workout_plan_id,
                user_id=user_id,
                exercise_plan_id=exercise_plan_id,
            )

        # 2. Get the current maximum order in set number.
        max_set_number = await self.repos.session.scalar(
            select(sqlfunc.max(ExerciseSetPlan.set_number)).where(
                ExerciseSetPlan.exercise_plan_id == exercise_plan_id
            )
        )

        # 3. Validate the new set number.
        new_set_number = payload.set_number
        # 3.a Update Scenario: we are updaing currently existing exercise set plan
        if old_set_plan and new_set_number > max_set_number:
            raise HTTPException(
                status_code=400,
                detail=f"set_number passed {new_set_number} is not valid, "
                f"set_number should not exceed {max_set_number}.",
            )
        # 3.b Create scenario: validate the set_number
        if max_set_number and payload.set_number > (max_set_number + 1):
            raise HTTPException(
                status_code=400,
                detail=f"set_number passed {payload.set_number} is not valid, "
                f"the next available set number is {max_set_number + 1}",
            )
        # 3.c First time adding a set, make sure the set_number = 1
        if not max_set_number and new_set_number > 1:
            raise HTTPException(
                status_code=400,
                detail=f"set_number passed {new_set_number} is larger than 1",
            )

        # when updating, fix order for others
        session = self.repos.session
        if old_set_plan:
            old_order = old_set_plan.set_number
            if new_set_number < old_order:
                # Moving item up (e.g., from order 5 to order 2)
                # Increment order_in_plan for items that were between new_order and old_order-1
                await session.execute(
                    update(ExerciseSetPlan)
                    .where(
                        ExerciseSetPlan.exercise_plan_id == exercise_plan_id,
                        ExerciseSetPlan.set_number >= new_set_number,
                        ExerciseSetPlan.set_number < old_order,
                        ExerciseSetPlan.id
                        != exercise_set_plan_id,  # Exclude the target item itself
                    )
                    .values(set_number=ExerciseSetPlan.set_number + 1)
                )
            elif new_set_number > old_order:  # new_order > old_order
                # Moving item down (e.g., from order 2 to order 5)
                # Decrement order_in_plan for items that were between old_order+1 and new_order
                await session.execute(
                    update(ExerciseSetPlan)
                    .where(
                        ExerciseSetPlan.exercise_plan_id == exercise_plan_id,
                        ExerciseSetPlan.set_number > old_order,
                        ExerciseSetPlan.set_number <= new_set_number,
                        ExerciseSetPlan.id
                        != exercise_set_plan_id,  # Exclude the target item itself
                    )
                    .values(set_number=ExerciseSetPlan.set_number - 1)
                )
        else:
            await session.execute(
                update(ExerciseSetPlan)
                .where(
                    ExerciseSetPlan.exercise_plan_id == exercise_plan_id,
                    ExerciseSetPlan.set_number >= payload.set_number,
                )
                .values(set_number=ExerciseSetPlan.set_number + 1)
            )
        # If all validations pass, call the original function.
        print("All validations passed. Proceeding with original function logic.")
        return await func(
            self,
            *args,
            **kwargs,
        )

    return wrapper
