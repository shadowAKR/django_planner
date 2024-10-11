import logging
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.conf import settings

from .models import Subjects
from management.models import Dropdown

logger = logging.getLogger(__name__)

# Create your views here.


class LearnDashboard(TemplateView):
    template_name = "learn_dashboard.html"
    
    def get(self,  request, *args, **kwargs):
        """get method"""
        # genai.configure(api_key=settings.AI_SECRET)
        # model = genai.GenerativeModel("gemini-1.5-flash")
        # response = model.generate_content("Write a story about a magic backpack.")
        your_subjects = Subjects.objects.filter(user=request.user)
        all_subjects = Dropdown.objects.filter(model_name="subjects", field="name")
        
        return render(
            request,
            template_name=self.template_name,
            context={
                "your_subjects": your_subjects,
                "all_subjects": all_subjects,
                "view": "home"
            }
        )

