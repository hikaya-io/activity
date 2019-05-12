#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Report, ReportAdmin


admin.site.register(Report, ReportAdmin)
