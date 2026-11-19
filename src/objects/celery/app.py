from django.conf import settings

from celery import Celery
from django_structlog.celery.steps import DjangoStructLogInitStep
from maykin_common.health_checks.celery.probes import EventLoopProbe
from maykin_common.logging.celery import setup_celery_structlog

app = Celery("objects")
app.config_from_object("django.conf:settings", namespace="CELERY")

setup_celery_structlog(format_exc_info=settings.LOG_FORMAT_CONSOLE == "json")

assert app.steps is not None
app.steps["worker"].add(DjangoStructLogInitStep)
app.steps["worker"].add(EventLoopProbe)

app.autodiscover_tasks()
