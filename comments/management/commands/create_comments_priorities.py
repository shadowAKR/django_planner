"""
Author: Ananathu Krishnan
Date: 11-June-2024
"""

import logging
from django.core.management.base import BaseCommand
from management.models import Dropdown


logger = logging.getLogger(__name__)

VALUES = ["Low", "Medium", "High", "Critical"]
ORDER = [1, 2, 3, 4]

COLOR = ["#C8E4B2", "#9ED2BE", "#7EAA92", "#FFD9B7"]


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            model_name = "comment"
            field = "priority"
            Dropdown.objects.filter(model_name=model_name, field=field).hard_delete()
            for value, order, color in zip(VALUES, ORDER, COLOR):
                Dropdown.objects.create(
                    model_name=model_name,
                    field=field,
                    value=value,
                    order=order,
                    color=color,
                )
            return "success"
        except Exception as error:
            logger.exception("Error while inserting record. Error: %s", error)
            return "failed"
