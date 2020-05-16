#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .views import (
    ReportData, IndicatorReportData, CollectedDataReportData, ProjectReportData,
    IndicatorTrackingHome, GenerateReport
)
from django.urls import path, re_path


# place app url patterns here

urlpatterns = [
    # display reports
    path('indicator_tracking/', IndicatorTrackingHome.as_view(), name='indicator_tracking_home'),
    path('report_data/project/', ProjectReportData.as_view(),
         name='project_report_data'),
    path('report_data/indicator/', IndicatorReportData.as_view(),
         name='indicator_report_data'),
    path('report_data/collecteddata/', CollectedDataReportData.as_view(),
         name='collecteddata_report_data'),
    path('report_data/', ReportData.as_view(), name='report_data'),


    re_path(
          r'quarterly_report/(?P<program_id>.*)/(?P<reporting_id>.*)',
          GenerateReport.as_view(),
          name='quarterly_report'
    ),
]
