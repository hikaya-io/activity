from django.db import models
from formlibrary.models import Service


class Distribution(Service):
    """
    Distribution of items, or group of items, to individuals or households
    Subject to future changes: https://github.com/hikaya-io/activity/issues/419
    """
    # ? How would we handle a distribution of multiple objects? (A medical kit for example)
    item_distributed = models.CharField(max_length=255, null=False, blank=False)
    quantity = models.IntegerField(verbose_name="Number of items distributed")
