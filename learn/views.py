import logging
import datetime
import google.generativeai as genai
from google.generativeai import caching
from django.shortcuts import render, redirect
from django.utils.html import strip_tags
from django.contrib import messages
from django.views.generic import ListView, View
from django.conf import settings

from .models import Courses, Learn, Question, Assessments
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


class LearnCourse(View):
    """learn view"""

    template_name = "learn.html"

    def get(self, request, *args, **kwargs):
        """get method"""
        course_object_id = self.kwargs.get("course_object_id")
        start_learning = str(request.GET.get("start_learning")).lower() == "true"
        if start_learning:
            course_dropdown = Dropdown.objects.get(
                field="name", model_name="courses", object_id=course_object_id
            )
            levels = Dropdown.objects.filter(field="level").order_by("order")
            course = Courses.objects.create(
                name=course_dropdown,
                current_level=levels[0],
                target_level=levels[1],
                user=request.user,
                start_date=datetime.datetime.now().date(),
            )
        else:
            course = Courses.objects.get(object_id=course_object_id)

        current_level = course.current_level.value
        course_name = course.name.value
        gen_ai_question = (
            f"Heading of a {current_level} level granular topic for learning {course_name} in an h3 tag."
        )
        already_know_topics = list(
            Learn.objects.filter(user=request.user, course=course).values_list(
                "topic", flat=True
            )
        )
        if already_know_topics:
            already_know_topics_text = ", ".join(already_know_topics)
            gen_ai_question = (
                gen_ai_question
                + f" I already know these topics: {already_know_topics_text}, "
                "so no need to explain it now."
            )
        genai.configure(api_key=settings.AI_SECRET)
        genai_model = genai.GenerativeModel("gemini-1.5-flash")
        new_topic = genai_model.generate_content(gen_ai_question)
        
        # # Create a cache with a 5 minute TTL
        # cache = caching.CachedContent.create(
        #     model='models/gemini-1.5-flash-001',
        #     display_name=f"{new_topic.text[:100]}", # used to identify the cache
        #     system_instruction=(
        #         'You are an expert teacher, and your job is to teach '
        #         'the user about the topic you have access to.'
        #     ),
        #     contents=[new_topic.text],
        #     ttl=datetime.timedelta(minutes=1),
        # )
        # # Construct a GenerativeModel which uses the created cache.
        # genai_model = genai.GenerativeModel.from_cached_content(cached_content=cache)
        main_topic = strip_tags(new_topic.text)
        topic_content = genai_model.generate_content(
            f"Define this topic {main_topic}, "
            "with some examples in proper html tags that starts from a div and style with tailwind css. "
            "Currently I'm using dark theme in tailwind css."
            "I'm showing the output in a div tag under an html page i already have, "
            f"so no need for <html>, ```html, ``` in the output. No need to main topic heading in the output. "
        )
        Learn.objects.create(
            topic=main_topic,
            content=topic_content.text,
            user=request.user,
            course=course,
        )
        return render(
            request,
            self.template_name,
            {
                "course": course,
                "topic": main_topic,
                "content": topic_content.text,
                "view": "learn",
            },
        )


class TakeAssessment(View):
    """Assessment take view"""

    template_name = "take_assessment.html"

    def get(self, request, *args, **kwargs):
        """get method"""
        course_object_id = self.kwargs.get("course_object_id")

        genai.configure(api_key=settings.AI_SECRET)
        genai_model = genai.GenerativeModel("gemini-1.5-flash")
        generate_content = genai_model.generate_content(
            f"A description of course, within 200 words"
        )
        generate_content.text
        return render(request=request, template_name=self.template_name, context={})
