from fastapi import Depends
from app.api.v1.categories.service import CategoryService
from app.api.v1.exercises.service import ExerciseService
from app.api.v1.muscle_groups.service import MuscleGroupService
from app.api.v1.sessions.services.workout_session_service import WorkoutSessionService
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

def get_muscle_group_service(all_repos: Repos = Depends(get_all_repos)):
    return MuscleGroupService(repos=all_repos)

def get_category_service(all_repos: Repos = Depends(get_all_repos)):
    return CategoryService(repos=all_repos)

def get_session_service(all_repos: Repos = Depends(get_all_repos)):
    return WorkoutSessionService(repos=all_repos)