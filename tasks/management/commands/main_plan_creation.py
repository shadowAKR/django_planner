"""
Author: Ananathu Krishnan
Date: 11-June-2024
"""

import logging
from django.core.management.base import BaseCommand
from management.models import Dropdown
from ...models import Plan


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            Plan.objects.filter(title="Main").hard_delete()
            plan = Plan(
                title="Main",
                description="Sample Plan",
                status=Dropdown.objects.only("id").get(model_name="plan",field="status",value="In Progress"),
            )
            plan.save()
            return "success"
        except Exception as error:
            logger.exception("Error while inserting record. Error: %s", error)
            return "failed"
