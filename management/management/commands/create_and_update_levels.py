"""
Author: Ananthu Krishnan
Date: 30 September 2024
"""
import logging

from django.core.management.base import BaseCommand

from utils.colors import generate_random_color
from ...models import Dropdown


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """command runner class"""
    help = "Create or update level dropdowns"
    
    values = [
        "Novice",
        "Beginnner",
        "Intermediate",
        "Advanced",
        "Expert",
        "Master",
        "Legendary",
    ]

    def handle(self, *args, **options):
        try:
            for order, value in enumerate(self.values, start=1):
                drop_obj = Dropdown.objects.filter(field="level", value=value).first()
                if drop_obj:
                    drop_obj.order = order
                    drop_obj.save(update_fields=["order"])
                else:
                    Dropdown.objects.create(
                        value=value,
                        order=order,
                        field="level",
                        color=generate_random_color(),
                    )
            return "success"
        except Exception as error:
            logger.exception("Error while creating or updating levels: %s", error)
            return "failed"