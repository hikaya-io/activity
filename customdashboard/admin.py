#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    ProgramLinks, Link, ProgramNarratives, JupyterNotebooks
)


class GalleryAdmin(admin.ModelAdmin):
    change_form_template = 'customdashboard/admin/change_form.html'


@admin.register(ProgramLinks)
class ProgramLinksAdmin(admin.ModelAdmin):
    list_display = ('program', 'create_date', 'edit_date')
    display = 'Program Link'


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'create_date', 'edit_date')
    display = 'Link'


@admin.register(ProgramNarratives)
class ProgramNarrativesAdmin(admin.ModelAdmin):
    list_display = ('narrative', 'create_date', 'edit_date')
    display = 'Overlay Narrative'


@admin.register(JupyterNotebooks)
class JupyterNotebooksAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'very_custom_dashboard',
                    'create_date', 'edit_date')
    display = 'Jupyter Notebooks'
