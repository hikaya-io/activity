#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import models
from .service import Service
from .service import CreatedModifiedBy, StartEndDates


class Construction(Service, CreatedModifiedBy, StartEndDates):
    """
    Service of a construction project.
    Not yet used model.
    """
    # implementer = stakeholder
    status = models.CharField(max_length=255)
