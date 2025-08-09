from celery.app import Celery

from app.core.config import settings

redis_server = settings.REDIS_SERVER

celery_app = Celery(__name__, broker=redis_server, backend=redis_server)

celery_app.conf.update(
    imports=["app.worker.tasks"],
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)
if settings.ENV == "dev":
    print("Purged celery tasks")
    celery_app.control.purge()

celery_app.conf.timezone = "UTC"
