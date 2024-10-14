from django.urls import path
from . import  views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login-view"),
    path("register/", views.RegisterView.as_view(), name="register-view"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("user-info/", views.GetUserInfo.as_view(), name="get-user-info-view"),
]
