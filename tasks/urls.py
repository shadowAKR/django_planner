from django.urls import path
from . import  views

urlpatterns = [
    path("", views.TaskView.as_view(), name="tasks"),
    path("plan/<str:object_id>/", views.TaskView.as_view(), name="plan-tasks"),
]
