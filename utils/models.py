#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
NB: ONLY abstract models are located here.
"""

import uuid
from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from workflow.models import ActivityUser


class StartEndDates(models.Model):
    """
    Abstract Base Class to implement start/end dates fields
    """
    # TODO move to its own place. A package named "core_mixins"
    # TODO Check the start_date < end_date and throw adequate error if else
    # TODO Will we need the same for a Slug field? Does Django offer one?
    start_date = models.DateTimeField(verbose_name="Start date", null=True, blank=True)
    end_date = models.DateTimeField(verbose_name="End date", null=True, blank=True)

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
    create_date = models.DateTimeField(verbose_name="Creation date", null=True, blank=True)
    modified_date = models.DateTimeField(verbose_name="Last Modification date", null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Create/Edit dates in UTC timezone
        """
        if self.create_date is None:
            self.create_date = datetime.utcnow()
        self.modified_date = datetime.utcnow()
        super().save(*args, **kwargs)


class CreatedModifiedBy(models.Model):
    # TODO implement logic of setting these values
    created_by = models.ForeignKey(ActivityUser, null=True, editable=True,
                                    verbose_name="Created by", related_name="+", on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, null=True,  editable=True,
                                    verbose_name="Last Modified by", related_name="+", on_delete=models.SET_NULL)

    class Meta:
        abstract = True
