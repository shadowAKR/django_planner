import logging
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView
from django.conf import settings

from .models import Courses
from management.models import Dropdown

logger = logging.getLogger(__name__)

# Create your views here.


class UserCourses(ListView):
    model = Courses
    context_object_name = "your_courses"
    template_name = "home.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Courses.objects.filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__value__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["view"] = "home"
        return context


class AllCourses(ListView):
    model = Dropdown
    context_object_name = "all_courses"
    template_name = "courses.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Dropdown.objects.filter(model_name="courses", field="name")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(value__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["view"] = "courses"
        return context
