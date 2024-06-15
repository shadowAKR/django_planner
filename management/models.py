import uuid
from django.db import models
from django.conf import settings
from safe_delete.models import SoftDeletionModel

# Create your models here.


class GenericFields(SoftDeletionModel):
    """Audit fields"""

    object_id = models.UUIDField(
        unique=True,
        editable=False,
        db_index=True,
        default=uuid.uuid4,
        verbose_name="Public identifier",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_created",
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_updated",
        null=True, blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class Dropdown(GenericFields):
    value = models.CharField(max_length=100, db_index=True)
    color = models.CharField(max_length=10)
    order = models.PositiveIntegerField(null=True, default=0)
    model_name = models.CharField(max_length=100)
    field = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.value} | {self.field} | {self.model_name}"
