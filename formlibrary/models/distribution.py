#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from workflow.models import Program, ProjectAgreement, Office, Province


class Distribution(models.Model):
    """
    Distribution of items, or group of items, to individuals or households
    Subject to future changes: https://github.com/hikaya-io/activity/issues/419
    """
    distribution_name = models.CharField(max_length=255)
    program = models.ForeignKey(
        Program, null=True, blank=True, on_delete=models.SET_NULL)
    initiation = models.ForeignKey(ProjectAgreement, null=True, blank=True,
                                   verbose_name="Project Initiation",
                                   on_delete=models.SET_NULL)
    office_code = models.ForeignKey(
        Office, null=True, blank=True, on_delete=models.SET_NULL)
    distribution_indicator = models.CharField(max_length=255)
    distribution_implementer = models.CharField(
        max_length=255, null=True, blank=True)
    reporting_period = models.CharField(max_length=255, null=True, blank=True)
    province = models.ForeignKey(
        Province, null=True, blank=True, on_delete=models.SET_NULL)
    total_individuals_received_input = models.IntegerField(
        null=True, blank=True)
    distribution_location = models.CharField(
        max_length=255, null=True, blank=True)
    input_type_distributed = models.CharField(
        max_length=255, null=True, blank=True)
    distributor_name_and_affiliation = models.CharField(
        max_length=255, null=True, blank=True)
    distributor_contact_number = models.CharField(
        max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    form_filled_by = models.CharField(max_length=255, null=True, blank=True)
    form_filled_by_position = models.CharField(
        max_length=255, null=True, blank=True)
    form_filled_by_contact_num = models.CharField(
        max_length=255, null=True, blank=True)
    form_filled_date = models.CharField(max_length=255, null=True, blank=True)
    form_verified_by = models.CharField(max_length=255, null=True, blank=True)
    form_verified_by_position = models.CharField(
        max_length=255, null=True, blank=True)
    form_verified_by_contact_num = models.CharField(
        max_length=255, null=True, blank=True)
    form_verified_date = models.CharField(
        max_length=255, null=True, blank=True)
    total_received_input = models.CharField(
        max_length=255, null=True, blank=True)
    total_male = models.IntegerField(null=True, blank=True)
    total_female = models.IntegerField(null=True, blank=True)
    total_age_0_14_male = models.IntegerField(null=True, blank=True)
    total_age_0_14_female = models.IntegerField(null=True, blank=True)
    total_age_15_24_male = models.IntegerField(null=True, blank=True)
    total_age_15_24_female = models.IntegerField(null=True, blank=True)
    total_age_25_59_male = models.IntegerField(null=True, blank=True)
    total_age_25_59_female = models.IntegerField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('distribution_name',)

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Distribution, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.distribution_name
