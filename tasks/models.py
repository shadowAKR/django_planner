"""Tasks app models"""

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from management.models import GenericFields, Dropdown
from accounts.models import User, Teams
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
    planned_start_date = models.DateField(blank=True, null=True)
    planned_end_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    owners = models.ManyToManyField(
        User, blank=True, db_index=True, related_name="%(app_label)s_%(class)s_owners"
    )
    active = models.BooleanField(default=False, blank=True)
    
    def __str__(self):
        return str(self.title)

@receiver(post_save, sender=Plan)
def plan_post_save(sender, instance, created, **kwargs):
    """
    Post save updates for plan object
    """
    if created:
        Plan.objects.filter(active=True).update(active=False)
        instance.active = True
        instance.save(update_fields=["active"])
    else:
        if instance.active:
            Plan.objects.filter(active=True).exclude(id=instance.id).update(active=False)
    


class Tasks(GenericFields):
    """
    Tasks model
    """
    title = models.CharField(max_length=500, db_index=True)
    description = models.TextField(blank=True, null=True, db_index=True)
    plan = models.ForeignKey(
        Plan, null=True, related_name="%(app_label)s_%(class)s_plan",
        on_delete=models.SET_NULL
    )
    team = models.ForeignKey(Teams, null=True, related_name="%(app_label)s_%(class)s_team",
        on_delete=models.SET_NULL
    )
    status = models.ForeignKey(
        Dropdown, null=True, blank=True, related_name="%(app_label)s_%(class)s_status",
        on_delete=models.SET_NULL
    )
    priority = models.ForeignKey(
        Dropdown, null=True, blank=True, related_name="%(app_label)s_%(class)s_priority",
        on_delete=models.SET_NULL
    )
    planned_start_date = models.DateField(blank=True, null=True)
    planned_end_date = models.DateField(blank=True, null=True)
    estimated_work_hours = models.PositiveIntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    worked_hours = models.JSONField(default=dict)
    owners = models.ManyToManyField(
        User, blank=True, db_index=True, related_name="%(app_label)s_%(class)s_owners"
    )
    comments = models.ManyToManyField(
        Comment, blank=True, related_name="%(app_label)s_%(class)s_comments"
    )
    
    def __str__(self):
        return str(self.title)
