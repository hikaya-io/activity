from .views import *
from django.conf.urls import *


# place app url patterns here

urlpatterns = [

                       # display reports
                       url(r'^report/$', ReportHome.as_view(), name='report_home'),
                       url(r'^report_data/project/$', ProjectReportData.as_view(), name='project_report_data'),
                       url(r'^report_data/indicator/$', IndicatorReportData.as_view(), name='indicator_report_data'),
                       url(r'^report_data/collecteddata/$', CollectedDataReportData.as_view(), name='collecteddata_report_data'),
                       url(r'^report_data/$', ReportData.as_view(), name='report_data'),

                       ]
