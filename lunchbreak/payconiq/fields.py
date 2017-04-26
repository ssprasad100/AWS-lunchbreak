from django.db import models
from Lunchbreak.fields import StatusSignalMixin


class StatusSignalCharField(StatusSignalMixin, models.CharField):
    pass
