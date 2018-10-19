from django.contrib import admin
from .models import *
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from tola.util import getCountry


admin.site.register(CustomDashboard, CustomDashboardAdmin)
admin.site.register(DashboardTheme, DashboardThemeAdmin)
admin.site.register(DashboardComponent, DashboardComponentAdmin)
admin.site.register(ComponentDataSource, ComponentDataSourceAdmin)
