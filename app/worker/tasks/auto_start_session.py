import asyncio
from sqlalchemy import select
from app.core.database.async_session_maker import AsyncSessionMaker
from app.models import WorkoutSession, WorkoutSessionStatus
from ..celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="auto_start_session")
def start_scheduled_session(session_id: int):
    logger.info(f"Attempting to start scheduled session: {session_id}")

    async def get_and_start_session():
        async with AsyncSessionMaker() as session:
            try:
                workout_session = await session.scalar(
                    select(WorkoutSession).where(WorkoutSession.id == session_id)
                )

                if not workout_session:
                    logger.info(f"Workout session with id: {session_id} not found")
                    return f"Failed to start session with id: {session_id}"

                workout_session.status = WorkoutSessionStatus.in_progress

                await session.commit()
            except Exception as e:
                logger.info(f"Failed to start session: {e}")
                await session.rollback()
            finally:
                await session.close()

    running_loop = asyncio.get_event_loop()
    running_loop.run_until_complete(get_and_start_session())    
    return f"Executed starting session with id: {session_id}"
