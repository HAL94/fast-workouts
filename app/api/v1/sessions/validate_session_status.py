import logging
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WorkoutSession, WorkoutSessionStatus

logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.INFO)


async def is_session_status_valid(session: AsyncSession, session_id: int, user_id: int):
    try:
        found_session = await session.scalar(
            select(WorkoutSession).where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.id == session_id,
                WorkoutSession.status != WorkoutSessionStatus.scheduled,
                WorkoutSession.status != WorkoutSessionStatus.cancelled,
            )
        )

        if not found_session:
            raise HTTPException(
                status_code=403,
                detail="Session should be in-progress or completed for adding results",
            )

        return True

    except Exception as e:
        logger.info(f"Error occured validating session status: {e}")
        raise HTTPException(
            status_code=403,
            detail="Session should be in-progress or completed for adding results",
        )
