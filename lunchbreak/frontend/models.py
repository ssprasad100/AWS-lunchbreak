import uuid

import jsonfield
from django.db import models


class Forward(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    group = models.CharField(
        max_length=191
    )
    json = jsonfield.JSONField(
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    def __str__(self):
        return str(self.id)
