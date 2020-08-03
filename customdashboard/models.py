#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import models
from workflow.models import Program


LINK_TYPE_CHOICES = (
    ('gallery', 'Gallery'),
    ('map', 'MapBox Map Layer'),
)


class ProgramNarratives(models.Model):
    program = models.ForeignKey(
        Program, blank=True, null=True, on_delete=models.SET_NULL)
    narrative_title = models.CharField(
        "Narrative Title", max_length=100, blank=True)
    narrative = models.TextField("Narrative Text", blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.narrative_title


class Link(models.Model):
    link = models.CharField("Link to Service", max_length=200, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.link


class ProgramLinks(models.Model):
    program = models.ForeignKey(
        Program, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField("Type of Link", blank=True,
                            null=True, max_length=255,
                            choices=LINK_TYPE_CHOICES)
    link = models.ForeignKey(Link, max_length=200,
                             blank=True, null=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)


class JupyterNotebooks(models.Model):
    name = models.CharField("Notebook Name", max_length=255)
    program = models.ForeignKey(
        Program, blank=True, null=True, on_delete=models.SET_NULL)
    very_custom_dashboard = models.CharField(
        "Specialty Custom Dashboard Links", blank=True, null=True,
        max_length=255)
    file = models.FileField("HTML/Jupyter Nontebook File",
                            blank=True, null=True, upload_to="media")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Jupyter Notebooks"

    def __str__(self):

        return self.name
