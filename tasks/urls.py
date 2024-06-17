from django.urls import path
from . import  views

urlpatterns = [
    path("", views.TaskView.as_view(), name="tasks"),
    path("create-task/", views.TaskCreateView.as_view(), name="task-create"),
    path("plan/<str:object_id>/", views.TaskView.as_view(), name="plan-tasks"),
]
