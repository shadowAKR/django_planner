from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from management.models import GenericFields
from .functions import generate_pastel_hex
# Create your models here.


class Teams(GenericFields):
    name = models.CharField(max_length=250)
    color = models.CharField(max_length=10)

class User(AbstractUser, GenericFields):
    """user model"""
    email = models.EmailField(unique=True)
    dob = models.DateField(blank=True, null=True)
    school = models.TextField(blank=True, null=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, blank=True, null=True)
    designation = models.CharField(max_length=250, blank=True, null=True)
    full_name = models.CharField(max_length=300, blank=True)
    fav_color = models.CharField(max_length=10, blank=True, null=True)
    profile_pic = models.ImageField(
        upload_to="profile_pic", default="profile_pic/default_profile_pic.png",
        blank=True
        )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

@receiver(post_save, sender=User)
def plan_post_save(sender, instance, created, **kwargs):
    """
    Post save updates for user object
    """
    if not instance.full_name:
        instance.full_name = f"{instance.first_name} {instance.last_name}".strip()
        instance.fav_color = generate_pastel_hex()
        instance.save(update_fields=["full_name"])