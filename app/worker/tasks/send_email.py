
from datetime import datetime
from ..celery_app import celery_app


@celery_app.task(name="send_workout_reminder_email")
def reminder_email(schedule_id: int | None = None):
    print(f"{datetime.now().isoformat()}")
    print(f"Running reminder email for schedule_id: {schedule_id}")
    print("Dummy task completed")
    return "Dummy task completed"
