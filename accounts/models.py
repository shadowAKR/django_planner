from django.db import models
from django.contrib.auth.models import AbstractUser

from management.models import GenericFields
# Create your models here.

class Teams(GenericFields):
    name = models.CharField(max_length=250)
    color = models.CharField(max_length=10)


class User(AbstractUser, GenericFields):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, blank=True, null=True)
    designation = models.CharField(max_length=250, blank=True, null=True)
