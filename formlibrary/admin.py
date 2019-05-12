#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .models import *

admin.site.register(TrainingAttendance, TrainingAttendanceAdmin)
admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Beneficiary, BeneficiaryAdmin)
