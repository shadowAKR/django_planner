from django.db import models
from django.conf import settings
from safe_delete.models import SoftDeletionModel
# Create your models here.

class GenericFields(SoftDeletionModel):
    """ Audit fields"""
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
        null=True,
    )
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

class Dropdown(GenericFields):
    value = models.CharField(max_length=100, db_index=True)
    color = models.CharField(max_length=10)
    order = models.PositiveIntegerField(null=True, default=0)
    model_name = models.CharField(max_length=100)
    field = models.CharField(max_length=100)
