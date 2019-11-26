#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .views import (home, import_table)
from django.urls import path


# place app url patterns here

urlpatterns = [
    # display import
    path('home/', home, name='home'),
    path('import_table/', import_table, name='import_table'),
]
