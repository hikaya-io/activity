from .views import (
  ProgramList, PublicDashboard, SurveyPublicDashboard, 
  SurveyTalkPublicDashboard, RRIMAPublicDashboard, 
  Notebook, DefaultCustomDashboard, 
  DefaultCustomDashboard, DefaultCustomDashboard
)

from django.urls import path, re_path


# place app url patterns here

urlpatterns = [

    #display public custom dashboard
    path('program_list/<slug:pk>/', ProgramList.as_view(), name='program_list'),
    path('program_dashboard/<slug:id>/<slug:public>/', PublicDashboard, name='public_dashboard'),
    path('public/<slug:id>/', PublicDashboard, name='public_dashboard'),
    re_path(r'^public/(?P<id>\w+)/([0-9]+)/$', PublicDashboard, name='public_dashboard'),

    #Extermely custom dashboards
    path('survey_public/', SurveyPublicDashboard, name='survey_public_dashboard'),
    path('survey_talk_public/', SurveyTalkPublicDashboard, name='survey_talk_public_dashboard'),

    #rimma
    path('rrima/', RRIMAPublicDashboard, name='rrima_public_dashboard'),

    #jupyternotebooks (For RIMMA now but could be used for any program as well)
    path('notebook/<slug:id>/', Notebook, name='notebook'),

    #display default custom dashboard
    path('<slug:id>/', DefaultCustomDashboard, name='default_custom_dashboard'),
    re_path(r'^(?P<id>\w+)/([0-9]+)/$', DefaultCustomDashboard, name='default_custom_dashboard'),

    #project status
    re_path(r'^(?P<id>[0-9]+)/(?P<status>[\w ]+)/$', DefaultCustomDashboard, name='project_status'),

]
