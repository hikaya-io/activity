#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    CustomDashboard, DashboardComponent, DashboardTheme, ComponentDataSource
)


@admin.register(CustomDashboard)
class CustomDashboardAdmin(admin.ModelAdmin):
    list_display = ('dashboard_name', 'dashboard_description', 'is_public',
                    'theme', 'color_palette', 'create_date', 'edit_date')
    display = 'Custom Dashboard'


@admin.register(DashboardTheme)
class DashboardThemeAdmin(admin.ModelAdmin):
    list_display = ('theme_name', 'theme_description', 'is_public',
                    'number_of_components', 'layout_dictionary', 'create_date',
                    'edit_date')
    display = 'Dashboard Theme'


@admin.register(DashboardComponent)
class DashboardComponentAdmin(admin.ModelAdmin):
    list_display = ('component_name', 'component_description',
                    'component_type', 'data_required', 'create_date',
                    'edit_date')
    display = 'Dashboard Components'


@admin.register(ComponentDataSource)
class ComponentDataSourceAdmin(admin.ModelAdmin):
    list_display = ('data_name', 'data_type', 'data_source',
                    'data_filter_key', 'create_date', 'edit_date')
    display = 'Data Source'
