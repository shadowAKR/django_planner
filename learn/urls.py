from django.urls import path
from . import  views

urlpatterns = [
    path("", views.UserSubjects.as_view(), name="home"),
    path("learn/", views.AllSubjects.as_view(), name="all-subjects"),
]
