from django.apps import apps
from django.db import models


class NotifyQuerySet(models.QuerySet):

    def notify(self, message, **kwargs):
        kwargs.setdefault('sound', 'default')
        model_name = self.model.__name__
        token_model = apps.get_model(
            'business.{model}Token'.format(
                model=model_name
            )
        )

        token_model.objects.filter(
            **{
                model_name.lower() + '__in': self
            }
        ).send_message(
            message,
            **kwargs
        )


class StaffManager(models.Manager):

    def get_queryset(self):
        return NotifyQuerySet(
            self.model,
            using=self._db
        )
