#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import models
from .service import Service


class Construction(Service):
    """
    Service of a construction project.
    Not yet used model.
    """
    # implementer = stakeholder
    status = models.CharField(max_length=255)
