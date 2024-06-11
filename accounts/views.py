import logging
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.views.generic import View, TemplateView
from .models import User

logger = logging.getLogger("__name__")

# Create your views here.


class LoginView(TemplateView):
    template_name = "login_form.html"

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(email=email, password=password).exists():
            return redirect("/")
        return render(request, template_name="login_form.html")


class RegisterView(TemplateView):
    """
    User register view
    """
    template_name = "register_form.html"

    def post(self, request):
        """
        post method
        """
        try:
            email = request.POST.get("email")
            password = request.POST.get("password")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            logger.info(username)
            if User.objects.filter(username=username).exists():
                messages.info(request, "A user with same username already exists!")
                return redirect("/accounts/register/")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "A user with same email already exists!")
                return redirect("/accounts/register/")
            else:
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.set_password(password)
                user.save()
                messages.success(request, "User created successfully.")
                return redirect("/accounts/login/")
        except Exception as error:
            print(f"Error while registering user: {error}")
            return redirect("/accounts/register/")
