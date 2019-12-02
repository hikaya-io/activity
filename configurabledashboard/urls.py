#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.urls import path, re_path

from .views import (
    CustomDashboardCreate, CustomDashboardDelete, CustomDashboardDetail,
    CustomDashboardList, CustomDashboardUpdate, custom_dashboard_update_components,
    DashboardComponentCreate, DashboardComponentDelete, DashboardComponentList,
    DashboardComponentUpdate, DashboardThemeCreate, DashboardThemeDelete,
    DashboardThemeList, DashboardThemeUpdate, ComponentDataSourceList,
    ComponentDataSourceCreate, ComponentDataSourceDelete, ComponentDataSourceDetail,
    ComponentDataSourceUpdate,
)


urlpatterns = [
    path('<int:pk>/', CustomDashboardList.as_view(),
         name='custom_dashboard_list'),
    path('detail/<int:pk>/', CustomDashboardDetail.as_view(),
         name='custom_dashboard_detail'),
    path('add/<int:pk>/', CustomDashboardCreate.as_view(),
         name='custom_dashboard_add'),
    path('update/<int:pk>/', CustomDashboardUpdate.as_view(
        template_name="configurabledashboard/dashboard/form.html"),
         name='custom_dashboard_update'),
    path('edit/<int:pk>/', CustomDashboardUpdate.as_view(
        template_name="configurabledashboard/dashboard/modal_form.html"),
         name='custom_dashboard_edit'),
    re_path(r'map/(?P<pk>[0-9]+)/(?P<location>[0-9]+)/(?P<type>[-\w]+)/$',
            custom_dashboard_update_components,
            name='custom_dashboard_update_components'),
    re_path(r'remap/(?P<pk>[0-9]+)/(?P<location>[0-9]+)/(?P<type>[-\w]+)/$',
            CustomDashboardUpdate.as_view(
                template_name="configurabledashboard/"
                              "components/admin/remap.html"),
            name='custom_dashboard_unmap'),
    path('delete/<int:pk>/', CustomDashboardDelete.as_view(),
         name='custom_dashboard_delete'),

    path('theme/', DashboardThemeList.as_view(), name='dashboard_theme_list'),
    path('theme_add/', DashboardThemeCreate.as_view(),
         name='dashboard_theme_add'),
    path('theme_update/<int:pk>/', DashboardThemeUpdate.as_view(),
         name='custom_dashboard/theme_update'),
    path('theme_delete/<int:pk>/', DashboardThemeDelete.as_view(),
         name='custom_dashboard/theme_delete'),

    path('component/<int:pk>/', DashboardComponentList.as_view(),
         name='dashboard_component_list'),
    path('component_add/<int:id>/', DashboardComponentCreate.as_view(),
         name='custom_dashboard/component_add'),
    path('component_update/<int:pk>/', DashboardComponentUpdate.as_view(
        template_name="configurabledashboard/components/"
                      "admin/update_form.html"),
         name='custom_dashboard/component_update'),
    path('component_delete/<int:pk>/', DashboardComponentDelete.as_view(),
         name='custom_dashboard/component_delete'),

    path('data/<int:pk>/', ComponentDataSourceList.as_view(),
         name='component_data_source_list'),
    path('data_add/', ComponentDataSourceCreate.as_view(),
         name='custom_dashboard/data_add'),
    path('data_detail/<int:pk>/', ComponentDataSourceDetail.as_view(),
         name='custom_data_source_detail'),
    path('data_assign/<int:pk>/', DashboardComponentUpdate.as_view(
        template_name="configurabledashboard/datasource/assign.html"),
         name='custom_dashboard/data_assign'),
    path('data_update/<int:pk>/', ComponentDataSourceUpdate.as_view(),
         name='custom_dashboard/data_update'),
    path('data_delete/<int:pk>/', ComponentDataSourceDelete.as_view(),
         name='custom_dashboard/data_delete'),
]
