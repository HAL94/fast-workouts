from celery.app import Celery

from app.core.config import settings

redis_server = settings.REDIS_SERVER

celery_app = Celery(__name__, broker=redis_server, backend=redis_server)

celery_app.conf.update(imports=['app.worker.tasks'])

celery_app.conf.timezone = 'UTC'