import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from .models import Tasks, Plan
from management.models import Dropdown


class TaskView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_object_id = self.kwargs.get("object_id", None)
        if plan_object_id:
            plan_obj = Plan.objects.only("id", "title").get(object_id=plan_object_id)
        else:
            plan_obj = Plan.objects.only("id", "title").get(active=True)
        task_type = self.request.GET.get("task_type", None)
        if task_type == "ongoing_tasks":
            context["task_type"] = "Ongoing tasks"
            filters = {
                "status": Dropdown.objects.only("id").get(
                    model_name="tasks", field="status", value="In Progress"
                ),
                "plan": plan_obj,
            }
        elif task_type == "important_tasks":
            context["task_type"] = "Important tasks"
            filters = {
                "priority": Dropdown.objects.only("id").get(
                    model_name="tasks", field="priority", value="Critical"
                ),
                "plan": plan_obj,
            }
        elif task_type == "completed_tasks":
            context["task_type"] = "Completed tasks"
            filters = {
                "status": Dropdown.objects.only("id").get(
                    model_name="tasks", field="status", value="Completed"
                ),
                "plan": plan_obj,
            }
        elif task_type == "uncompleted_tasks":
            context["task_type"] = "Uncompleted tasks"
            filters = {
                "status__in": Dropdown.objects.only("id").filter(
                    model_name="tasks",
                    field="status",
                    value__in=["Open", "In Progress"],
                ),
                "plan": plan_obj,
            }
        else:
            context["task_type"] = "All tasks"
            filters = {
                "plan": plan_obj,
            }
        
        all_plans_list = list(Plan.objects.only("id", "object_id", "title").exclude(id=plan_obj.id).order_by("-modified_date"))
        all_plans_list.insert(0, plan_obj)
        context["plans_dropdown"] = all_plans_list
        context["tasks"] = Tasks.objects.only("id","object_id").filter(**filters).order_by("-modified_date")
        context["plan_object_id"] = plan_object_id

        context["user"] = self.request.user
        return context
