from .views import *
from django.conf.urls import *


# place app url patterns here

urlpatterns = patterns('',

                       #display import
                       url(r'^home/$', 'tables.views.home', name='home'),
                       url(r'^import_table/$', 'tables.views.import_table', name='import_table'),
                       )