from django.db import models
from accounts.models import User
from management.models import GenericFields, Dropdown

# Create your models here.


class Courses(GenericFields):
    """Courses model"""

    name = models.ForeignKey(
        Dropdown,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_name",
        null=True,
        blank=True,
    )
    current_level = models.ForeignKey(
        Dropdown,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_current_level",
        null=True,
        blank=True,
    )
    target_level = models.ForeignKey(
        Dropdown,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_target_level",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_user",
        null=True,
        blank=True,
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

class Learn(GenericFields):
    """Learn model"""
    topic = models.CharField(max_length=300, db_index=True)
    content = models.TextField(db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_user",
        null=True,
        blank=True,
    )
    course = models.ForeignKey(
        Courses,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_course",
        null=True,
        blank=True,
    )
    verified = models.BooleanField(default=False)

class Question(GenericFields):
    """Question model"""

    title = models.TextField(blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    hint = models.TextField(blank=True, null=True)
    correct_answer = models.TextField(blank=True, null=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_user",
        null=True,
        blank=True,
    )
    attended = models.BooleanField(default=False, blank=True)
    user_answer = models.TextField(blank=True, null=True, db_index=True)
    correct = models.BooleanField(blank=True, default=False, db_index=True)
    ai_response = models.TextField(blank=True, null=True)
    learn_content = models.ForeignKey(
        Learn,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_learn_content",
        null=True,
        blank=True,
    )


class Assessments(GenericFields):
    """Assessment model"""

    title = models.CharField(max_length=250, blank=True, null=True, db_index=True)
    attained_score = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    max_score = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    questions = models.ManyToManyField(
        Question, related_name="%(app_label)s_%(class)s_questions", blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_user",
        null=True,
        blank=True,
    )
    level = models.ForeignKey(
        Dropdown,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_level",
        null=True,
        blank=True,
    )
    subject = models.ForeignKey(
        Courses,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_subject",
        null=True,
        blank=True,
    )
    attended_date = models.DateField(blank=True, null=True)
    ai_response = models.TextField(blank=True, null=True)
