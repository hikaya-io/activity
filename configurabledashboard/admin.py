#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .models import *


admin.site.register(CustomDashboard, CustomDashboardAdmin)
admin.site.register(DashboardTheme, DashboardThemeAdmin)
admin.site.register(DashboardComponent, DashboardComponentAdmin)
admin.site.register(ComponentDataSource, ComponentDataSourceAdmin)
