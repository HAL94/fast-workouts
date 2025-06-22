from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.repositories import (
    Repos,
    WorkoutPlanRepository,
    ExercisePlanRepository,
    ExerciseSetPlanRepository,
)
from app.dependencies.database import get_async_session

def get_all_repos(session: AsyncSession = Depends(get_async_session)):
    return Repos(session=session)
    

def get_exercise_plan_repo(session: AsyncSession = Depends(get_async_session)):
    return ExercisePlanRepository(session)


def get_exercise_set_plan_repo(session: AsyncSession = Depends(get_async_session)):
    return ExerciseSetPlanRepository(session)


def get_workout_plan_repo(
    session: AsyncSession = Depends(get_async_session),
    exercise_plan_repo: ExercisePlanRepository = Depends(get_exercise_plan_repo),
    exercise_set_plan_repo: ExerciseSetPlanRepository = Depends(
        get_exercise_set_plan_repo
    ),
):
    return WorkoutPlanRepository(
        session,
        exercise_plan_repo,
        exercise_set_plan_repo,
    )
