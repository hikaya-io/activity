#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .views import *
from django.urls import path


# place app url patterns here

urlpatterns = [
    # display reports
    path('report/', ReportHome.as_view(), name='report_home'),
    path('report_data/project/', ProjectReportData.as_view(),
         name='project_report_data'),
    path('report_data/indicator/', IndicatorReportData.as_view(),
         name='indicator_report_data'),
    path('report_data/collecteddata/', CollectedDataReportData.as_view(),
         name='collecteddata_report_data'),
    path('report_data/', ReportData.as_view(), name='report_data'),
]
