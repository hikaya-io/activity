from __future__ import unicode_literals
from django.db import models
from django.contrib import admin
from datetime import datetime
from workflow.models import Program, SiteProfile, ProjectAgreement, Office, Province

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone


class TrainingAttendance(models.Model):
    training_name = models.CharField(max_length=255)
    program = models.ForeignKey(Program, null=True, blank=True)
    project_agreement = models.ForeignKey(ProjectAgreement, null=True, blank=True, verbose_name="Project Initiation")
    implementer = models.CharField(max_length=255, null=True, blank=True)
    reporting_period = models.CharField(max_length=255, null=True, blank=True)
    total_participants = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    community = models.CharField(max_length=255, null=True, blank=True)
    training_duration = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.CharField(max_length=255, null=True, blank=True)
    end_date = models.CharField(max_length=255, null=True, blank=True)
    trainer_name = models.CharField(max_length=255, null=True, blank=True)
    trainer_contact_num = models.CharField(max_length=255, null=True, blank=True)
    form_filled_by = models.CharField(max_length=255, null=True, blank=True)
    form_filled_by_contact_num = models.CharField(max_length=255, null=True, blank=True)
    total_male = models.IntegerField(null=True, blank=True)
    total_female = models.IntegerField(null=True, blank=True)
    total_age_0_14_male = models.IntegerField(null=True, blank=True)
    total_age_0_14_female = models.IntegerField(null=True, blank=True)
    total_age_15_24_male = models.IntegerField(null=True, blank=True)
    total_age_15_24_female = models.IntegerField(null=True, blank=True)
    total_age_25_59_male = models.IntegerField(null=True, blank=True)
    total_age_25_59_female = models.IntegerField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('training_name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(TrainingAttendance, self).save()

    # displayed in admin templates
    def __unicode__(self):
        return unicode(self.training_name)


class TrainingAttendanceAdmin(admin.ModelAdmin):
    list_display = ('training_name', 'program', 'project_agreement', 'create_date', 'edit_date')
    display = 'Training Attendance'
    list_filter = ('program__country','program')


class Distribution(models.Model):
    distribution_name = models.CharField(max_length=255)
    program = models.ForeignKey(Program, null=True, blank=True)
    initiation = models.ForeignKey(ProjectAgreement, null=True, blank=True, verbose_name="Project Initiation")
    office_code = models.ForeignKey(Office, null=True, blank=True)
    distribution_indicator = models.CharField(max_length=255)
    distribution_implementer = models.CharField(max_length=255, null=True, blank=True)
    reporting_period = models.CharField(max_length=255, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True)
    total_beneficiaries_received_input = models.IntegerField(null=True, blank=True)
    distribution_location = models.CharField(max_length=255, null=True, blank=True)
    input_type_distributed = models.CharField(max_length=255, null=True, blank=True)
    distributor_name_and_affiliation = models.CharField(max_length=255, null=True, blank=True)
    distributor_contact_number = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    form_filled_by = models.CharField(max_length=255, null=True, blank=True)
    form_filled_by_position = models.CharField(max_length=255, null=True, blank=True)
    form_filled_by_contact_num = models.CharField(max_length=255, null=True, blank=True)
    form_filled_date = models.CharField(max_length=255, null=True, blank=True)
    form_verified_by = models.CharField(max_length=255, null=True, blank=True)
    form_verified_by_position = models.CharField(max_length=255, null=True, blank=True)
    form_verified_by_contact_num = models.CharField(max_length=255, null=True, blank=True)
    form_verified_date = models.CharField(max_length=255, null=True, blank=True)
    total_received_input = models.CharField(max_length=255, null=True, blank=True)
    total_male = models.IntegerField(null=True, blank=True)
    total_female = models.IntegerField(null=True, blank=True)
    total_age_0_14_male = models.IntegerField(null=True, blank=True)
    total_age_0_14_female = models.IntegerField(null=True, blank=True)
    total_age_15_24_male = models.IntegerField(null=True, blank=True)
    total_age_15_24_female = models.IntegerField(null=True, blank=True)
    total_age_25_59_male = models.IntegerField(null=True, blank=True)
    total_age_25_59_female = models.IntegerField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('distribution_name',)

    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Distribution, self).save()

    # displayed in admin templates
    def __unicode__(self):
        return unicode(self.distribution_name)


class DistributionAdmin(admin.ModelAdmin):
    list_display = ('distribution_name', 'program', 'initiation', 'create_date', 'edit_date')
    display = 'Program Dashboard'


class Beneficiary(models.Model):
    beneficiary_name = models.CharField(max_length=255, null=True, blank=True)
    training = models.ManyToManyField(TrainingAttendance, blank=True)
    distribution = models.ManyToManyField(Distribution, blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    site = models.ForeignKey(SiteProfile, null=True, blank=True)
    signature = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    program = models.ManyToManyField(Program, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('beneficiary_name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Beneficiary, self).save()

    # displayed in admin templates
    def __unicode__(self):
        return unicode(self.beneficiary_name)


class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('site','beneficiary_name',)
    display = 'Beneficiary'
    list_filter = ('site','beneficiary_name')