#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    TrainingAttendance, Distribution, Individual
)


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    list_display = ('site', 'beneficiary_name',)
    display = 'Individual'
    list_filter = ('site', 'beneficiary_name')


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ('distribution_name', 'program',
                    'initiation', 'create_date', 'edit_date')
    display = 'Program Dashboard'


@admin.register(TrainingAttendance)
class TrainingAttendanceAdmin(admin.ModelAdmin):
    list_display = ('training_name', 'program',
                    'project_agreement', 'create_date', 'edit_date')
    display = 'Training Attendance'
    list_filter = ('program__country', 'program')
