#!/usr/bin/python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from django.db import models
from workflow.models import Program, Office, Stakeholder, Site, Contact, ActivityUser
from .case import Case
from django.core.exceptions import ValidationError


class StartEndDates(models.Model):
    """
    Abstract Base Class to implement start/end dates fields
    """
    # TODO move to its own place. A package named "core_mixins"
    # TODO Check the start_date < end_date and throw adequate error if else
    # TODO Will we need the same for a Slug field? Does Django offer one?
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def save(self, **kwargs):
        self.clean()
        return super(StartEndDates, self).save(**kwargs)

    def clean(self):
        # ? What if only a single date is supplied? Should the start/end date
        # ? Be higher/lower than today's date?
        super(StartEndDates, self).clean()
        if None not in (self.start_date, self.end_date) and self.end_date < self.start_date:
            raise ValidationError("Sorry, End date must be greater than start date.")

    class Meta:
        abstract = True


class CreatedModifiedDates(models.Model):
    "Mixins for created/modified timestamps"
    # TODO Unit test this
    # This is the naming used in other models
    create_date = models.DateTimeField(verbose_name="Creation date", editable=False,
                                        null=False, blank=False, auto_now_add=True)
    modified_date = models.DateTimeField(verbose_name="Modification date", editable=False,
                                        null=False, blank=False, auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Create/Edit dates in UTC timezone
        """
        if self.create_date is None:
            self.create_date = datetime.utcnow()
        self.edit_date = datetime.utcnow()
        super().save(*args, **kwargs)


class CreatedModifiedBy(models.Model):
    # TODO implement logic of setting these values
    created_by = models.ForeignKey(ActivityUser, null=True, editable=False,
                                    verbose_name="Created by", related_name="+", on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, null=True,  editable=False,
                                    verbose_name="Modified by", related_name="+", on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class Service(CreatedModifiedBy, CreatedModifiedDates, StartEndDates, models.Model):
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
    form_completed_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ('name',)

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