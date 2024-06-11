import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from .models import User


class TaskView(TemplateView):
    template_name = "home.html"
