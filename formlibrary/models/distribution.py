#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from formlibrary.models import Service


class Distribution(Service):
    """
    Distribution of items, or group of items, to individuals or households
    Subject to future changes: https://github.com/hikaya-io/activity/issues/419
    """
    # ? How is the item stored? CharField? Does it belong to an inventory?
    item_distributed = models.CharField(max_length=255, null=False, blank=False)
    quantity = models.IntegerField(verbose_name="Number of items distributed", default=0)

    # displayed in admin templates
    def __str__(self):
        return "Distribution: " + self.name
