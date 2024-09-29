from django.urls import path
from . import  views

urlpatterns = [
    path("", views.LearnDashboard.as_view(), name="home"),
]
