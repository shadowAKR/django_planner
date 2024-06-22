import logging, datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, View
from .models import Tasks, Plan
from accounts.models import User, Teams
from urllib.parse import urlencode
from comments.models import Comment
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
        context["user_completed_task_count"] = (
            Tasks.objects.only("id")
            .filter(owners=self.request.user,status__value="Completed")
            .count()
        )
        context["user_total_task_count"] = (
            Tasks.objects.only("id")
            .filter(owners=self.request.user)
            .count()
        )

        return context


class TaskCreateView(TemplateView):
    """
    Task create view
    """

    template_name = "task-create.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.GET.get("plan_object_id"):
            plan = Plan.objects.only("id", "title").get(
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
        all_plans = list(
            Plan.objects.only("id", "title").order_by("-id").exclude(id=plan.id)
        )
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


class TaskDetailView(TemplateView):
    template_name = "task-detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        task_object_id = self.kwargs.get("object_id")
        comment_added = self.request.GET.get("comment_added")
        task = Tasks.objects.get(object_id=task_object_id)
        context["task"] = task
        context["comment_added"] = True if comment_added == "true" else False
        new_comments = task.comments.exclude(
                viewed_users_ids__contains=self.request.user.id
            )
        context["comment_not_viewed_count"] = new_comments.count()
        for new_comment in new_comments:
            new_comment.viewed_users_ids.append(self.request.user.id)
            new_comment.save(update_fields=["viewed_users_ids"])
        return context


class TaskUpdateView(TemplateView):
    template_name = "task-edit.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        task_object_id = self.kwargs.get("object_id")
        context["task"] = Tasks.objects.get(object_id=task_object_id)
        context["statuses"] = Dropdown.objects.filter(
            model_name="tasks", field="status"
        ).only("id", "value")
        context["priorities"] = Dropdown.objects.filter(
            model_name="tasks", field="priority"
        ).only("id", "value")
        context["owners"] = User.objects.filter(
            is_active=True, is_superuser=False
        ).only("id", "full_name")
        context["plans"] = Plan.objects.only("id", "title").order_by("-id")
        context["teams"] = Teams.objects.only("id", "name").all()
        return context

    def post(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("object_id")
        try:
            task = Tasks.objects.get(object_id=task_object_id)
            task.title = self.request.POST.get("title")
            task.description = self.request.POST.get("description")
            task.status_id = (
                int(self.request.POST.get("status"))
                if self.request.POST.get("status")
                else None
            )
            task.priority_id = (
                int(self.request.POST.get("priority"))
                if self.request.POST.get("priority")
                else None
            )
            owners = self.request.POST.getlist("owners")
            task.planned_start_date = (
                self.request.POST.get("planned_start_date")
                if self.request.POST.get("planned_start_date")
                else None
            )
            task.planned_end_date = (
                self.request.POST.get("planned_end_date")
                if self.request.POST.get("planned_end_date")
                else None
            )
            task.start_date = (
                self.request.POST.get("start_date")
                if self.request.POST.get("start_date")
                else None
            )
            task.end_date = (
                self.request.POST.get("end_date")
                if self.request.POST.get("end_date")
                else None
            )
            task.estimated_work_hours = (
                int(self.request.POST.get("estimated_work_hours"))
                if self.request.POST.get("estimated_work_hours")
                else None
            )
            task.save()
            task.owners.set(owners)
            messages.success(request=request, message="Task updated successfully.")
        except Exception as error:
            print(error)
            logger.info("Error while creating task: %s", error)
            messages.error(request=request, message="Task updation failed.")
        if task:
            return redirect("plan-tasks", task.plan.object_id)
        return redirect("tasks")


class TaskDeleteView(View):
    template_name = "task-detail.html"

    def post(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("object_id")
        task = Tasks.objects.get(object_id=task_object_id)
        plan_object_id = task.plan.object_id
        task.delete()
        messages.success(request=request, message="Task deleted successfully.")
        return redirect("plan-tasks", plan_object_id)


class AddCommentView(View):

    def post(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("object_id")
        try:
            comment = self.request.POST.get("comment")
            priority = self.request.POST.get("priority", None)
            task = Tasks.objects.get(object_id=task_object_id)
            if comment:
                comment_obj = Comment.objects.create(
                    text=comment,
                    resolved=False,
                    priority=priority,
                    created_by=self.request.user,
                    created_date=datetime.datetime.now()
                )
                task.comments.add(comment_obj)
        except Exception as error:
            logger.info("Error while adding comment: %s", error)
        url = reverse(
            "task-detail", kwargs={"object_id": task.object_id}
        )
        url = f"{url}?{urlencode({"comment_added":"true"})}"
        return redirect(url)
