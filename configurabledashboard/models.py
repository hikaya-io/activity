from __future__ import unicode_literals

from django.db import models
from django.contrib import admin
from datetime import datetime
from workflow.models import Program

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone


class DashboardTheme(models.Model):
    theme_name = models.CharField("Dashboard Theme Name", max_length=255, blank=True)
    theme_description = models.TextField("Brief Description", null=True, blank=True, help_text="What is the focus of this theme?")
    theme_template = models.CharField("Template", max_length=255, blank=True)
    is_public = models.BooleanField(default=False)
    number_of_components = models.IntegerField(blank=False, null=False, default=1)
    layout_dictionary = models.TextField("Dashboard Layout Dictionary", null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('theme_name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(DashboardTheme, self).save()

    # displayed in admin templates
    def __unicode__(self):
        return self.theme_name


class DashboardThemeAdmin(admin.ModelAdmin):
    list_display = ('theme_name', 'theme_description', 'is_public', 'number_of_components', 'layout_dictionary','create_date', 'edit_date')
    display = 'Dashboard Theme'


class ComponentDataSource(models.Model):
    data_name = models.CharField("Name of Source Data", max_length=255, blank=True)
    data_type = models.CharField("Data Type", max_length=200, null=True, blank=True, help_text="Is this data photos? Text? Numerical data?")
    data_source = models.URLField(max_length=200, null=True, blank=True)
    data_source_type = models.CharField("Data Source Type", max_length=200, null=True, blank=True)
    data_filter_key = models.CharField("Key Term", max_length=255, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('id',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(ComponentDataSource, self).save()

    # displayed in admin templates
    def __unicode__(self):
        return self.data_name


class ComponentDataSourceAdmin(admin.ModelAdmin):
    list_display = ('data_name', 'data_type','data_source','data_filter_key', 'create_date', 'edit_date')
    display = 'Data Source'


class DashboardComponent(models.Model):
    component_name = models.CharField("Component Name", max_length=255, blank=True)
    component_description = models.TextField("Brief Description", null=True, blank=True, help_text="What does this component do?")
    is_public = models.BooleanField("External Public Dashboard", default=False)
    component_type = models.CharField("Component Type", max_length=255, blank=True)
    data_required = models.CharField("Required Data Type", max_length=255, blank=False)
    data_sources = models.ManyToManyField(ComponentDataSource, blank=False, related_name="datasourceset")
    data_map = models.TextField("Data Mapping Dictionary", null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('component_name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(DashboardComponent, self).save()

    # displayed in admin templates
    def __unicode__(self):
        return self.component_name


class DashboardComponentAdmin(admin.ModelAdmin):
    list_display = ('component_name', 'component_description', 'component_type', 'data_required', 'create_date', 'edit_date')
    display = 'Dashboard Components'
# For programs that have custom dashboards. The default dashboard for all other programs is 'Program Dashboard'


class CustomDashboard(models.Model):
    dashboard_name = models.CharField("Custom Dashboard Name", max_length=255, blank=True)
    dashboard_description = models.TextField("Brief Description", null=True, blank=True, help_text="What does this custom dashboard display to the user?")
    is_public = models.BooleanField("External Public Dashboard", default=False)
    theme = models.ForeignKey(DashboardTheme, blank=True, null=True, related_name='theme')
    program = models.ForeignKey(Program, verbose_name="Program", related_name="dashboard_program", null=True, blank=True)
    color_palette = models.CharField("Color Scheme", max_length=255, blank=False, default="bright")
    components = models.ManyToManyField(DashboardComponent, blank=True, related_name="componentset")
    component_map = models.TextField("Dashboard Layout Dictionary", null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('dashboard_name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(CustomDashboard, self).save()

    # displayed in admin templates
    def __unicode__(self):
        return self.dashboard_name


class CustomDashboardAdmin(admin.ModelAdmin):
    list_display = ('dashboard_name', 'dashboard_description', 'is_public', 'theme', 'color_palette','create_date', 'edit_date')
    display = 'Custom Dashboard'