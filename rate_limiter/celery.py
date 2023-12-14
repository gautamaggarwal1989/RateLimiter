import logging
import os

from celery import shared_task
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rate_limiter.settings')
app = Celery(
    'rate_limiter',
    broker='redis://localhost:6379',
    include=["limiter.tasks"]
)
app.autodiscover_tasks()

# Configure the built-in Python logging module
logging.basicConfig(
    level='DEBUG',
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler('celery.log')]
)

# Configure your periodic task
app.conf.beat_schedule = {
    'my-periodic-task': {
        'task': 'limiter.tasks.refresh_bucket',
        'schedule': 1.0,
    },
}
