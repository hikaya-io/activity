#!/usr/bin/python3
# -*- coding: utf-8 -*-

from import_export import resources
from .models import TrainingAttendance, Distribution, Individual


class TrainingAttendanceResource(resources.ModelResource):

    class Meta:
        model = TrainingAttendance


class DistributionResource(resources.ModelResource):

    class Meta:
        model = Distribution


class IndividualResource(resources.ModelResource):

    class Meta:
        model = Individual
