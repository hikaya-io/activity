from .views import ProgramList, PublicDashboard, SurveyPublicDashboard, \
    SurveyTalkPublicDashboard, RRIMAPublicDashboard, Notebook, DefaultCustomDashboard, \
    DefaultCustomDashboard, DefaultCustomDashboard

from django.conf.urls import *


# place app url patterns here

urlpatterns = [

                       #display public custom dashboard
                       url(r'^program_list/(?P<pk>\w+)/$', ProgramList.as_view(), name='program_list'),
                       url(r'^program_dashboard/(?P<id>\w+)/(?P<public>\w+)/$', PublicDashboard, name='public_dashboard'),
                       url(r'^public/(?P<id>\w+)/$', PublicDashboard, name='public_dashboard'),
                       url(r'^public/(?P<id>\w+)/([0-9]+)/$', PublicDashboard, name='public_dashboard'),

                       #Extermely custom dashboards
                       url(r'^survey_public/$', SurveyPublicDashboard, name='survey_public_dashboard'),
                       url(r'^survey_talk_public/$', SurveyTalkPublicDashboard, name='survey_talk_public_dashboard'),

                       #rimma
                       url(r'^rrima/$', RRIMAPublicDashboard, name='rrima_public_dashboard'),

                       #jupyternotebooks (For RIMMA now but could be used for any program as well)
                       url(r'^notebook/(?P<id>\w+)/$', Notebook, name='notebook'),

                       #display default custom dashboard
                       url(r'^(?P<id>\w+)/$', DefaultCustomDashboard, name='default_custom_dashboard'),
                       url(r'^(?P<id>\w+)/([0-9]+)/$', DefaultCustomDashboard, name='default_custom_dashboard'),

                       #project status
                       url(r'^(?P<id>[0-9]+)/(?P<status>[\w ]+)/$', DefaultCustomDashboard, name='project_status'),

]
