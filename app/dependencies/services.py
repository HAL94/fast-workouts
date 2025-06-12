from fastapi import Depends
from app.api.v1.exercise_plans.service import ExercisePlanService
from app.api.v1.workouts.service import WorkoutPlanService
from app.repositories import WorkoutPlanRepository
from app.dependencies.repositories import get_exercise_plan_repo, get_exercise_set_plan_repo, get_workout_plan_repo
from app.repositories.exercise_plan_repository import ExercisePlanRepository
from app.repositories.exercise_set_plan_repository import ExerciseSetPlanRepository


def get_exercise_plan_service(
    exercise_plan_repo: ExercisePlanRepository = Depends(get_exercise_plan_repo),    
    exercise_set_plan_repo: ExerciseSetPlanRepository = Depends(get_exercise_set_plan_repo),
):
    return ExercisePlanService(exercise_plan_repo=exercise_plan_repo, exercise_set_plan_repo=exercise_set_plan_repo)


def get_workout_plan_service(
    workout_repo: WorkoutPlanRepository = Depends(get_workout_plan_repo),
):
    return WorkoutPlanService(workout_repo)
