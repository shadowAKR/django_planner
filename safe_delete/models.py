from django.db import models
from django.utils import timezone
from django.conf import settings

from safe_delete.managers import SoftDeletionManager


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_deleted",
        null=True, blank=True
    )

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()
