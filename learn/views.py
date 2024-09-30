import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.conf import settings

import google.generativeai as genai


logger = logging.getLogger("__name__")

# Create your views here.


class LearnDashboard(TemplateView):
    template_name = "learn_dashboard.html"
    
    def get(self,  request, *args, **kwargs):
        """get method"""
        genai.configure(api_key=settings.AI_SECRET)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Write a story about a magic backpack.")
        return render(request, template_name=self.template_name, context={"response": response})

