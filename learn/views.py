import logging
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView
from django.conf import settings

from .models import Subjects
from management.models import Dropdown

logger = logging.getLogger(__name__)

# Create your views here.


class UserSubjects(ListView):
    model = Subjects
    context_object_name = "your_subjects"
    template_name = "home.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Subjects.objects.filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__value__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["view"] = "home"
        return context


class AllSubjects(ListView):
    model = Dropdown
    context_object_name = "all_subjects"
    template_name = "learn.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Dropdown.objects.filter(model_name="subjects", field="name")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(value__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["view"] = "subjects"
        return context
