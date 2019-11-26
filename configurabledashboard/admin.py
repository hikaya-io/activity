#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    CustomDashboard, DashboardComponent, DashboardComponentAdmin, DashboardTheme,
    DashboardThemeAdmin, ComponentDataSource, ComponentDataSourceAdmin,
    CustomDashboardAdmin
)

admin.site.register(CustomDashboard, CustomDashboardAdmin)
admin.site.register(DashboardTheme, DashboardThemeAdmin)
admin.site.register(DashboardComponent, DashboardComponentAdmin)
admin.site.register(ComponentDataSource, ComponentDataSourceAdmin)
