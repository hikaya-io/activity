#!/usr/bin/python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from django.db import models
from workflow.models import Program, Office, Stakeholder, Site, Contact, ActivityUser
from .case import Case
from django.core.exceptions import ValidationError
from utils.models import CreatedModifiedBy, CreatedModifiedDates, StartEndDates


class Service(CreatedModifiedBy, CreatedModifiedDates, StartEndDates):
    """
    Abstract base class for all kinds of offered services.
    Spec: https://github.com/hikaya-io/activity/issues/412
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=550, null=True, blank=True)
    # Is a Program required for any type of service?
    program = models.ForeignKey(
        Program, null=True, blank=False, on_delete=models.SET_NULL)
    office = models.ForeignKey(
        Office, null=True, blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(
        Site, null=True, blank=True, on_delete=models.SET_NULL)
    # Can an implementer be in charge of multiple services?
    implementer = models.ForeignKey(
        Stakeholder, null=True, blank=True, on_delete=models.SET_NULL)
    # Cases relationship: Many To Many?
    cases = models.ManyToManyField(Case, blank=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    form_verified_by = models.CharField(max_length=255, null=True, blank=True)
    form_filled_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def total_individuals_supported(self):
        """
        Number of Individuals, excluding Households, supported by the service
        """
        # TODO Check all individuals, and households and their individuals
        return 0

    @property
    def total_households_supported(self):
        """
        Number of Households, supported by the service
        """
        # TODO Check all individuals, and households and their individuals
        return 0

    @property
    def total_supported(self):
        """
        Number of Individuals, including Households, supported by the service
        """
        # TODO Check all individuals, and households and their individuals
        return 0
