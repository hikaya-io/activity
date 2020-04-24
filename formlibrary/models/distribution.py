#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from workflow.models import Program, ProjectAgreement, Office, Province
from .service import Service

class Distribution(Service):
    """
    Distribution of items, or group of items, to individuals or households
    Subject to future changes: https://github.com/hikaya-io/activity/issues/419
    """
    initiation = models.ForeignKey(ProjectAgreement, null=True, blank=True,
                                   verbose_name="Project Initiation",
                                   on_delete=models.SET_NULL)
    indicator = models.CharField(max_length=255)
    reporting_period = models.CharField(max_length=255, null=True, blank=True)
    province = models.ForeignKey(
        Province, null=True, blank=True, on_delete=models.SET_NULL)
    total_individuals_received_input = models.IntegerField(
        null=True, blank=True)
    distribution_location = models.CharField(
        max_length=255, null=True, blank=True)
    input_type_distributed = models.CharField(
        max_length=255, null=True, blank=True)
    total_received_input = models.CharField(
        max_length=255, null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Distribution, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name
