
import resend
from datetime import datetime
from ..celery_app import celery_app
from app.core.config import settings


@celery_app.task(name="send_workout_reminder_email")
def reminder_email(schedule_id: int | None = None):
    print(f"{datetime.now().isoformat()}")
    print(f"Running reminder email for schedule_id: {schedule_id}")
    
    resend.api_key = settings.EMAIL_SERVICE

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "aftereffectxiii@gmail.com",
        "subject": "Prepare for your incoming workout",
        "html": f"<p>This is a reminder of your workout, scheduled id is: {schedule_id}!</p>"
    })

    return f"Email Reminder for schedule_id: {schedule_id} Sent!"
