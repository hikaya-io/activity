#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    TrainingAttendance, TrainingAttendanceAdmin, Distribution,
    DistributionAdmin, Beneficiary, BeneficiaryAdmin
)

admin.site.register(TrainingAttendance, TrainingAttendanceAdmin)
admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Beneficiary, BeneficiaryAdmin)
