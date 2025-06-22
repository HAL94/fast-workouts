from fastapi import Depends
from app.api.v1.workouts.service import WorkoutPlanService
from app.dependencies.repositories import get_all_repos
from app.repositories import Repos


def get_workout_plan_service(
    all_repos: Repos = Depends(get_all_repos),
):
    return WorkoutPlanService(repos=all_repos)
