#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    ProgramLinks, ProgramLinksAdmin, Link, LinkAdmin, ProgramNarratives,
    ProgramNarrativesAdmin, JupyterNotebooks, JupyterNotebooksAdmin
)


class GalleryAdmin(admin.ModelAdmin):
    change_form_template = 'customdashboard/admin/change_form.html'


admin.site.register(ProgramLinks, ProgramLinksAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(ProgramNarratives, ProgramNarrativesAdmin)
admin.site.register(JupyterNotebooks, JupyterNotebooksAdmin)
