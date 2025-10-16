from celery import Celery
from ..config import settings

app = Celery("fantasy")
app.conf.broker_url = settings.REDIS_URL
app.conf.result_backend = settings.REDIS_URL
app.conf.timezone = "UTC"