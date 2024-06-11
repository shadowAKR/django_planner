"""Tasks app models"""

from django.db import models
from management.models import GenericFields, Dropdown
from accounts.models import User
from comments.models import Comment

# Create your models here.


class Plan(GenericFields):
    """
    Plan model
    """
    title = models.CharField(max_length=500, db_index=True)
    description = models.TextField(blank=True, null=True, db_index=True)
    status = models.ForeignKey(
        Dropdown, null=True, blank=True, related_name="%(app_label)s_%(class)s_status",
        on_delete=models.SET_NULL
    )
    planned_start_date = models.DateTimeField(blank=True, null=True)
    planned_end_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    owners = models.ManyToManyField(
        User, blank=True, db_index=True, related_name="%(app_label)s_%(class)s_owners"
    )

class Tasks(GenericFields):
    """
    Tasks model
    """
    title = models.CharField(max_length=500, db_index=True)
    description = models.TextField(blank=True, null=True, db_index=True)
    status = models.ForeignKey(
        Dropdown, null=True, blank=True, related_name="%(app_label)s_%(class)s_status",
        on_delete=models.SET_NULL
    )
    priority = models.ForeignKey(
        Dropdown, null=True, blank=True, related_name="%(app_label)s_%(class)s_priority",
        on_delete=models.SET_NULL
    )
    planned_start_date = models.DateTimeField(blank=True, null=True)
    planned_end_date = models.DateTimeField(blank=True, null=True)
    estimated_work_hours = models.TimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    worked_hours = models.TimeField(blank=True, null=True)
    owners = models.ManyToManyField(
        User, blank=True, db_index=True, related_name="%(app_label)s_%(class)s_owners"
    )
    comments = models.ManyToManyField(
        Comment, blank=True, related_name="%(app_label)s_%(class)s_comments"
    )
