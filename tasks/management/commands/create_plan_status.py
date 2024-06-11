"""
Author: Ananathu Krishnan
Date: 11-June-2024
"""

import logging
from django.core.management.base import BaseCommand
from management.models import Dropdown


logger = logging.getLogger(__name__)

VALUES = ["Not Started", "Open", "In Progress", "Hold", "Completed"]
ORDER = [1, 2, 3, 4, 5]

COLOR = ["#2c2c2c", "#66BB66", "#f9b859", "#f27e3a", "#e53535"]


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            model_name = "plan"
            field = "status"
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
