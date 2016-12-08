from dirtyfields import DirtyFieldsMixin
from django.db import models


class StatusSignalModel(models.Model, DirtyFieldsMixin):

    class Meta:
        abstract = True

    def _get_FIELD_signal(self, field):
        value = getattr(self, field.attname)
        return field.signals[value]

    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields()
        # Currently does not support fields that are not named 'status'
        # This must be changed in case this is needed here.
        dirty_status = dirty_fields.get('status', None)

        signal = None
        if self.pk is None or dirty_status is not None:
            signal = self.get_status_signal()

        super().save(*args, **kwargs)

        if signal is not None:
            signal.send(
                **{
                    'sender': self.__class__,
                    # Assumes that the signal only has 1 argument
                    list(signal.providing_args)[0]: self
                }
            )
            self.status_changed()

    def status_changed(self):
        """Called when the status changes."""
        pass
