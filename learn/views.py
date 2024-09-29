import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView


logger = logging.getLogger("__name__")

# Create your views here.


class LearnDashboard(TemplateView):
    template_name = "learn_dashboard.html"
