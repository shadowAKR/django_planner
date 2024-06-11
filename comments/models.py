from django.db import models
from management.models import GenericFields, Dropdown

# Create your models here.


class Comment(GenericFields):
    """
    Comment model
    """

    text = models.TextField()
    priority = models.ForeignKey(
        Dropdown, null=True, blank=True, related_name="%(app_label)s_%(class)s_priority",
        on_delete=models.SET_NULL
    )
    resolved = models.BooleanField(blank=True, null=True)
