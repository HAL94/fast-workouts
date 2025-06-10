from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import WorkoutPlanRepository
from app.dependencies.database import get_async_session


def get_workout_plan_repo(session: AsyncSession = Depends(get_async_session)):
    return WorkoutPlanRepository(session)
