#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from workflow.models import Program, ProjectAgreement
from .service import StartEndDates


class TrainingAttendance(StartEndDates):
    training_name = models.CharField(max_length=255)
    program = models.ForeignKey(
        Program, null=True, blank=True, on_delete=models.SET_NULL)
    project_agreement = models.ForeignKey(
        ProjectAgreement, null=True, blank=True,
        verbose_name="Project Initiation", on_delete=models.SET_NULL)
    implementer = models.CharField(max_length=255, null=True, blank=True)
    reporting_period = models.CharField(max_length=255, null=True, blank=True)
    total_participants = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    community = models.CharField(max_length=255, null=True, blank=True)
    training_duration = models.CharField(max_length=255, null=True, blank=True)
    trainer_name = models.CharField(max_length=255, null=True, blank=True)
    trainer_contact_num = models.CharField(
        max_length=255, null=True, blank=True)
    form_filled_by = models.CharField(max_length=255, null=True, blank=True)
    form_filled_by_contact_num = models.CharField(
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
        ordering = ('training_name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(TrainingAttendance, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.training_name

# ? Attendance tracking needs more reflexion
# ? Tracking of attendance needs the notion of a session/class: track the `attendees`
# ? from the list of registered into the program
# class Attendance(models.Model):
#     """
#     Attendance "sheet" to keep track of Individuals/Household participations to trainings.
#     Spec: https://github.com/hikaya-io/activity/issues/422
#     """
#     number_of_sessions = models.IntegerField()
