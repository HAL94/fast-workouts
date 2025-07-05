from fastapi import Depends
from app.api.v1.exercises.services.exercise_service import ExerciseService
from app.api.v1.workouts.services import (
    ExercisePlanService,
    ExerciseSetPlanService,
    WorkoutScheduleService,
    WorkoutPlanService,
)


from app.dependencies.repositories import get_all_repos
from app.repositories import Repos


def get_workout_plan_service(
    all_repos: Repos = Depends(get_all_repos),
):
    return WorkoutPlanService(repos=all_repos)


def get_exercise_plan_service(
    all_repos: Repos = Depends(get_all_repos),
):
    return ExercisePlanService(repos=all_repos)


def get_exercise_set_plan_service(
    all_repos: Repos = Depends(get_all_repos),
):
    return ExerciseSetPlanService(repos=all_repos)


def get_schedule_service(
    all_repos: Repos = Depends(get_all_repos),
):
    return WorkoutScheduleService(repos=all_repos)


def get_exercise_service(all_repos: Repos = Depends(get_all_repos)):
    return ExerciseService(repos=all_repos)
