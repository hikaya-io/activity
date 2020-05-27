#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import models
from workflow.models import Contact
from .service import Service


class Training(Service):
    """
    Subject to future changes: https://github.com/hikaya-io/activity/issues/421
    ? Should we edit/update the already existing TrainingAttendance, or implement from scratch?
    """
    # ? Can a training have multiple trainers?
    # ? Can a trainer be in charge of multiple Trainings?
    trainer = models.ForeignKey(
        Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name="trainer_of")
    # ? Is this supplied in user input or calculated from start/end dates?
    duration = models.IntegerField(help_text="Number of days? Sessions?")

    # @property
    # def attendance(self):
    #     """
    #     ? Return list of Individuals and their attendance as a percentage relative to `training_duration`.
    #     """
    #     return {}
