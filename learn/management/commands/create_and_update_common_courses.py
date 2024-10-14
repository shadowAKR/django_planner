"""
Author: Ananthu Krishnan
Date: 30 September 2024
"""

import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from utils.colors import generate_random_color
from ...models import Dropdown
import google.generativeai as genai

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """command runner class"""

    help = "Create or update course dropdowns"

    values = [
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
    ]

    def handle(self, *args, **options):
        try:
            for order, value in enumerate(self.values, start=1):
                genai.configure(api_key=settings.AI_SECRET)
                genai_model = genai.GenerativeModel("gemini-1.5-flash")
                generate_content = genai_model.generate_content(f"A description of {value} course, within 200 words")
                drop_obj = Dropdown.objects.filter(field="name", model_name="courses", value=value).first()
                if drop_obj:
                    drop_obj.order = order
                    drop_obj.description = generate_content.text
                    drop_obj.color = generate_random_color()
                    drop_obj.save(update_fields=["order", "description", "color"])
                else:
                    Dropdown.objects.create(
                        value=value,
                        description=generate_content.text,
                        order=order,
                        field="name",
                        model_name="courses",
                        color=generate_random_color(),
                    )
            return "success"
        except Exception as error:
            logger.exception("Error while creating or updating levels: %s", error)
            return "failed"
