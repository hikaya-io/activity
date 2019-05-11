from django.db import models
from django.contrib import admin
from workflow.models import Program, ProjectAgreement, ProjectComplete, Country
from indicators.models import Indicator, CollectedData


class Report(models.Model):
    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.SET_NULL)
    program = models.ForeignKey(
        Program, null=True, blank=True, on_delete=models.SET_NULL)
    agreement = models.ForeignKey(
        ProjectAgreement, null=True, blank=True, on_delete=models.SET_NULL)
    complete = models.ForeignKey(
        ProjectComplete, null=True, blank=True, on_delete=models.SET_NULL)
    indicator = models.ForeignKey(
        Indicator, null=True, blank=True, on_delete=models.SET_NULL)
    collected = models.ForeignKey(
        CollectedData, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(
        "Status Description", max_length=200, blank=True)
    shared = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.program__name


class ReportAdmin(admin.ModelAdmin):
    list_display = ('country', 'program', 'description',
                    'create_date', 'edit_date')
    display = 'Project Status'
