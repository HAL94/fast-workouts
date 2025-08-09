import asyncio
import logging
import resend
from datetime import datetime

from sqlalchemy import select

from app.core.database.async_session_maker import AsyncSessionMaker
from app.models import ScheduleStatus, WorkoutPlanSchedule
from ..celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="send_workout_reminder_email")
def reminder_email(schedule_id: int | None = None):
    logger.info(f"{datetime.now().isoformat()}")
    logger.info(f"Running reminder email for schedule_id: {schedule_id}")

    resend.api_key = settings.EMAIL_SERVICE

    try:
        # Run the synchronous resend call in a separate thread to not block the event loop

        resend.Emails.send(
            {
                "from": "onboarding@resend.dev",
                "to": "aftereffectxiii@gmail.com",
                "subject": "Prepare for your incoming workout",
                "html": f"<p>This is a reminder of your workout, scheduled id is: {schedule_id}!</p>",
            }
        )
        logger.info(f"Email sent successfully for schedule_id: {schedule_id}")

    except Exception as e:
        logger.info(f"Error sending email for schedule_id {schedule_id}: {e}")
        return f"Email Reminder Failed: Error sending email. {e}"

    async def get_and_update_schedule():
        async with AsyncSessionMaker() as session:
            try:
                workout_schedule = await session.scalar(
                    select(WorkoutPlanSchedule).where(
                        WorkoutPlanSchedule.id == schedule_id
                    )
                )

                if not workout_schedule:
                    logger.info(f"Workout schedule with id {schedule_id} not found.")
                    # You might want to retry this task later or handle it differently
                    return f"Email Reminder Failed: Workout schedule {schedule_id} not found."

                logger.info(f"Fetched schedule entity: {workout_schedule}")

                workout_schedule.reminder_send_time = datetime.now()
                workout_schedule.reminder_status = ScheduleStatus.sent

                await session.commit()
                logger.info(f"Database updated for schedule_id: {schedule_id}")

            except Exception as e:
                await session.rollback()  # Rollback changes if an error occurs
                logger.info(f"Database error for schedule_id {schedule_id}: {e}")
                return f"Email Reminder Failed: Database error. {e}"
            finally:
                await session.close()

    running_loop = asyncio.get_event_loop()
    running_loop.run_until_complete(get_and_update_schedule())

    return f"Email Reminder for schedule_id: {schedule_id} Sent!"
