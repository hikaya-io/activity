#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .views import (
    ProgramList, public_dashboard, survey_public_dashboard,
    survey_talk_public_dashboard, rrima_public_dashboard,
    notebook, default_custom_dashboard
)

from django.urls import path, re_path

# place app url patterns here

urlpatterns = [
    # display public custom dashboard
    path('program_list/<slug:pk>/', ProgramList.as_view(),
         name='program_list'),
    path('program_dashboard/<slug:id>/<slug:public>/',
         public_dashboard, name='public_dashboard'),
    path('public/<slug:id>/', public_dashboard, name='public_dashboard'),
    re_path(r'^public/(?P<id>\w+)/([0-9]+)/$',
            public_dashboard, name='public_dashboard'),

    # Extermely custom dashboards
    path('survey_public/', survey_public_dashboard,
         name='survey_public_dashboard'),
    path('survey_talk_public/', survey_talk_public_dashboard,
         name='survey_talk_public_dashboard'),

    # rimma
    path('rrima/', rrima_public_dashboard, name='rrima_public_dashboard'),

    # jupyternotebooks (For RIMMA now but could be used
    # for any program as well)
    path('notebook/<slug:id>/', notebook, name='notebook'),

    # display default custom dashboard
    path('<slug:id>/', default_custom_dashboard,
         name='default_custom_dashboard'),
    re_path(r'^(?P<id>\w+)/([0-9]+)/$', default_custom_dashboard,
            name='default_custom_dashboard'),

    # project status
    re_path(r'^(?P<id>[0-9]+)/(?P<status>[\w ]+)/$',
            default_custom_dashboard, name='project_status'),

]
