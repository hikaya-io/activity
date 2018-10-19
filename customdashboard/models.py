from django.db import models
from django.contrib import admin
from django.conf import settings
from datetime import datetime

from workflow.models import Program


LINK_TYPE_CHOICES = (
    ('gallery', 'Gallery'),
    ('map', 'MapBox Map Layer'),
)


class ProgramNarratives(models.Model):
    program = models.ForeignKey(Program, blank=True)
    narrative_title = models.CharField("Narrative Title", max_length=100, blank=True)
    narrative = models.TextField("Narrative Text", blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.narrative_title


class ProgramNarrativesAdmin(admin.ModelAdmin):
    list_display = ('narrative', 'create_date', 'edit_date')
    display = 'Overlay Narrative'


class Link(models.Model):
    link = models.CharField("Link to Service", max_length=200, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.link


class LinkAdmin(admin.ModelAdmin):
    list_display = ('link','create_date','edit_date')
    display = 'Link'


class ProgramLinks(models.Model):
    program = models.ForeignKey(Program, blank=True)
    type = models.CharField("Type of Link",blank=True, null=True, max_length=255, choices=LINK_TYPE_CHOICES)
    link = models.ForeignKey(Link, max_length=200, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):

        return self.title


class ProgramLinksAdmin(admin.ModelAdmin):
    list_display = ('program','create_date','edit_date')
    display = 'Program Link'


class JupyterNotebooks(models.Model):
    name = models.CharField("Notebook Name", max_length=255)
    program = models.ForeignKey(Program, blank=True,null=True)
    very_custom_dashboard = models.CharField("Specialty Custom Dashboard Links",blank=True, null=True, max_length=255)
    file = models.FileField("HTML/Jupyter Nontebook File", blank=True,null=True,upload_to="media")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Jupyter Notebooks"

    def __unicode__(self):

        return self.name


class JupyterNotebooksAdmin(admin.ModelAdmin):
    list_display = ('name','program','very_custom_dashboard','create_date','edit_date')
    display = 'Jupyter Notebooks'

