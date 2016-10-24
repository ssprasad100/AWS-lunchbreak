from django.db import models

from .mixins import NotifyModelMixin


class NotifyQuerySet(models.QuerySet):

    def notify(self, message, **kwargs):
        return NotifyModelMixin._notify(
            message=message,
            queryset=self,
            **kwargs
        )


class StaffManager(models.Manager):

    def get_queryset(self):
        return NotifyQuerySet(
            self.model,
            using=self._db
        )
