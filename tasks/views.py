import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from .models import Tasks, Plan
from accounts.models import User, Teams
from management.models import Dropdown

logger = logging.getLogger("__name__")


class TaskView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
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

        all_plans_list = list(
            Plan.objects.only("id", "object_id", "title")
            .exclude(id=plan_obj.id)
            .order_by("-modified_date")
        )
        all_plans_list.insert(0, plan_obj)
        context["plans_dropdown"] = all_plans_list
        context["tasks"] = (
            Tasks.objects.only("id", "object_id")
            .filter(**filters)
            .order_by("-modified_date")
        )
        context["plan_object_id"] = plan_object_id

        context["user"] = self.request.user
        return context


class TaskCreateView(TemplateView):
    """
    Task create view
    """

    template_name = "task-create.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.GET.get("plan_object_id"):
            plan = Plan.objects.only("id").get(
                object_id=self.request.GET.get("plan_object_id")
            )
            context["plan"] = plan
            context["plan_object_id"] = self.request.GET.get("plan_object_id")
        else:
            plan = Plan.objects.only("id").get(active=True)
        context["statuses"] = Dropdown.objects.filter(
            model_name="tasks", field="status"
        ).only("id", "value")
        context["priorities"] = Dropdown.objects.filter(
            model_name="tasks", field="priority"
        ).only("id", "value")
        context["owners"] = User.objects.filter(
            is_active=True, is_superuser=False
        ).only("id", "full_name")
        all_plans = list(Plan.objects.only("id","title").order_by("-id").exclude(id=plan.id))
        all_plans.insert(0, plan)
        context["plans"] = all_plans
        context["teams"] = Teams.objects.only("id", "name").all()
        return context

    def post(self, request):
        plan_object_id = self.request.GET.get("plan_object_id")
        try:
            if plan_object_id:
                plan = Plan.objects.get(object_id=plan_object_id)
            else:
                plan = Plan.objects.get(active=True)
            title = self.request.POST.get("title")
            description = self.request.POST.get("description")
            status = (
                int(self.request.POST.get("status"))
                if self.request.POST.get("status")
                else None
            )
            priority = (
                int(self.request.POST.get("priority"))
                if self.request.POST.get("priority")
                else None
            )
            owners = self.request.POST.getlist("owners")
            planned_start_date = (
                self.request.POST.get("planned_start_date")
                if self.request.POST.get("planned_start_date")
                else None
            )
            planned_end_date = (
                self.request.POST.get("planned_end_date")
                if self.request.POST.get("planned_end_date")
                else None
            )
            estimated_work_hours = (
                int(self.request.POST.get("estimated_work_hours"))
                if self.request.POST.get("estimated_work_hours")
                else None
            )
            task = Tasks.objects.create(
                title=title,
                description=description,
                status_id=status,
                priority_id=priority,
                planned_start_date=planned_start_date,
                planned_end_date=planned_end_date,
                estimated_work_hours=estimated_work_hours,
                plan=plan,
            )
            task.owners.set(owners)
            messages.success(request=request, message="Task created successfully.")
        except Exception as error:
            print(error)
            logger.info("Error while creating task: %s", error)
            messages.error(request=request, message="Task creation failed.")
        if plan_object_id:
            return redirect("plan-tasks", plan_object_id)
        return redirect("tasks")
