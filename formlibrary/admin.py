#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    TrainingAttendance, Distribution, Individual, Training
)

admin.site.register(Training)


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    list_display = ('site', 'first_name',)
    display = 'Individual'


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'program',
        'create_date',
        'modified_date'
    )
    display = 'Program Dashboard'


@admin.register(TrainingAttendance)
class TrainingAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'training_name',
        'program',
        'project_agreement',
        'create_date',
        'edit_date'
    )
    display = 'Training Attendance'
    list_filter = ('program__country', 'program')
