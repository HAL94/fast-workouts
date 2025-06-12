from app.core.exceptions import NotFoundException
from app.models import WorkoutExercisePlan, WorkoutExerciseSetPlan
from app.repositories.exercise_plan_repository import ExercisePlanRepository
from app.repositories.exercise_set_plan_repository import ExerciseSetPlanRepository


class ExercisePlanService:
    def __init__(
        self,
        exercise_plan_repo: ExercisePlanRepository,
        exercise_set_plan_repo: ExerciseSetPlanRepository,
    ):
        self.exercise_plan_repo = exercise_plan_repo
        self.exercise_set_plan_repo = exercise_set_plan_repo

    async def find_exercise_plan_by_user_id(self, user_id: int, exercise_plan_id: int):
        result = await self.exercise_plan_repo.find_one_exercise_plan_by_user_id(
            user_id, exercise_plan_id=exercise_plan_id
        )
        if not result:
            raise NotFoundException(
                f"Could not find exercise plan with id: {exercise_plan_id}"
            )
        return result

    async def find_exercise_set_plan_by_user_id(
        self, user_id: int, exercise_set_plan_id: int
    ):
        result = (
            await self.exercise_set_plan_repo.find_one_exercise_set_plan_by_user_id(
                user_id, exercise_set_plan_id=exercise_set_plan_id
            )
        )
        if not result:
            raise NotFoundException(
                f"Could not find exercise set plan with id: {exercise_set_plan_id}"
            )
        return result

    async def create_exercise_plan(self, user_id: int, data: WorkoutExercisePlan):
        result = await self.exercise_plan_repo.create(
            data=WorkoutExercisePlan(**data.model_dump(), user_id=user_id)
        )
        return result

    async def delete_exercise_plan(self, exercise_plan_id: int):
        result = await self.exercise_plan_repo.delete_one(
            val=exercise_plan_id,
            where_clause=[
                WorkoutExercisePlan.id == exercise_plan_id,
            ],
        )
        return result

    async def delete_exercise_set_plan(self, exercise_set_plan_id: int):
        result = await self.exercise_set_plan_repo.delete_one(
            val=exercise_set_plan_id,
            where_clause=[
                WorkoutExerciseSetPlan.id == exercise_set_plan_id,
            ],
        )
        return result
