import logging
import traceback

from celery import Task
from django.conf import settings

logger = logging.getLogger('lunchbreak')


class DebugLoggingTask(Task):
    """Base Celery task for logging errors."""
    abstract = True

    def on_failure(self, exception, *args, **kwargs):
        """Log the exceptions to sentry."""

        if settings.DEBUG:
            traceback.print_exc()
        super().on_failure(exception, *args, **kwargs)
