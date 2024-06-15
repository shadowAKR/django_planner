from django.contrib import admin
from .models import Tasks, Plan

# Register your models here.

admin.site.register([Tasks, Plan])
