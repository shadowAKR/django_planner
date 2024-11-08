from django.urls import path
from . import  views

urlpatterns = [
    path("", views.UserCourses.as_view(), name="home"),
    path("all-courses/", views.AllCourses.as_view(), name="all-courses"),
    path("learn-course/<str:course_object_id>/", views.LearnCourse.as_view(), name="learn-course"),
]
