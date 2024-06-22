from django.urls import path
from . import  views

urlpatterns = [
    path("", views.TaskView.as_view(), name="tasks"),
    path("create-task/", views.TaskCreateView.as_view(), name="task-create"),
    path("task-detail/<str:object_id>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("update-task/<str:object_id>/", views.TaskUpdateView.as_view(), name="task-update"),
    path("delete-task/<str:object_id>/", views.TaskDeleteView.as_view(), name="task-delete"),
    path("plan/<str:object_id>/", views.TaskView.as_view(), name="plan-tasks"),
    path("add-task-comment/<str:object_id>/", views.AddCommentView.as_view(), name="add-task-comment"),
]
