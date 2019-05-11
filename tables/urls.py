from .views import *
from django.urls import path


# place app url patterns here

urlpatterns = [
    # display import
    path('home/', home, name='home'),
    path('import_table/', import_table, name='import_table'),
]
