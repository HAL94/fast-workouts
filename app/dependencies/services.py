from fastapi import Depends
from app.api.v1.workouts.service import WorkoutPlanService
from app.repositories import WorkoutPlanRepository
from app.dependencies.repositories import get_workout_plan_repo


def get_workout_plan_service(
    workout_repo: WorkoutPlanRepository = Depends(get_workout_plan_repo),
):
    return WorkoutPlanService(workout_repo)