from django.contrib import admin

from .models import *


class GalleryAdmin(admin.ModelAdmin):
    change_form_template = 'customdashboard/admin/change_form.html'

admin.site.register(ProgramLinks, ProgramLinksAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(ProgramNarratives, ProgramNarrativesAdmin)
admin.site.register(JupyterNotebooks, JupyterNotebooksAdmin)







