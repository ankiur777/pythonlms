import uuid

from django.db import models


class UUIDTimeStampedModel(models.Model):
    """Shared identity/timestamp convention documented in docs/DATABASE.md."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
