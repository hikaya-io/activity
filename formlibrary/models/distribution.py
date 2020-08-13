from django.db import models
from formlibrary.models import Service


class Distribution(Service):
    """
    Distribution of items, or group of items, to individuals or households
    Subject to future changes: https://github.com/hikaya-io/activity/issues/419
    """
    item_distributed = models.CharField(max_length=255, null=False, blank=False)
    quantity = models.IntegerField(verbose_name="Number of items distributed")

    def __str__(self):
        return "Distribution: " + self.name
