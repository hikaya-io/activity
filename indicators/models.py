#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.urls import reverse

import uuid
from simple_history.models import HistoricalRecords
from decimal import Decimal
from datetime import datetime, timedelta

from workflow.models import (
    Program, Sector, SiteProfile, ProjectAgreement, ProjectComplete,
    Country, Documentation, ActivityUser, Organization)


class ActivityTable(models.Model):
    name = models.CharField(max_length=255, blank=True)
    table_id = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(ActivityUser, on_delete=models.CASCADE)
    remote_owner = models.CharField(max_length=255, blank=True)
    country = models.ManyToManyField(Country, blank=True)
    url = models.CharField(max_length=255, blank=True)
    unique_count = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Activity Table'
        verbose_name_plural = 'Activity Tables'

    def __str__(self):
        return self.name


class IndicatorType(models.Model):
    indicator_type = models.CharField(max_length=135, blank=True)
    description = models.TextField(max_length=765, null=True, blank=True)
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('indicator_type',)
        verbose_name_plural = 'Indicator Types'

    def __str__(self):
        return self.indicator_type


class StrategicObjective(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)
    description = models.TextField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('country', 'name')
        verbose_name_plural = 'Strategic Objectives'

    def __str__(self):
        return self.name

    def save(self):
        if self.create_date is None:
            self.create_date = datetime.now()
        super(StrategicObjective, self).save()


class Objective(models.Model):
    name = models.CharField(max_length=135, blank=True)
    program = models.ForeignKey(
        Program, null=True, blank=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)
    description = models.TextField(max_length=765, blank=True)
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('program', 'name')

    def __str__(self):
        return '{}'.format(self.name) or ''


class Level(models.Model):
    name = models.CharField(max_length=135, blank=True)
    description = models.TextField(max_length=765, null=True, blank=True)
    sort = models.IntegerField(null=True, blank=True)
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('levels_list')


class DisaggregationType(models.Model):
    disaggregation_type = models.CharField(max_length=135, blank=True)
    description = models.CharField(max_length=765, blank=True)
    indicator = models.ForeignKey(
        'indicators.Indicator', on_delete=models.SET_NULL,
        related_name='disaggregation_label', null=True, blank=True)
    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.SET_NULL)
    standard = models.BooleanField(
        default=False, verbose_name="Standard (Activity Admins Only)")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = 'country', 'disaggregation_type'
        verbose_name = 'Disaggregation Type'
        verbose_name_plural = 'Disaggregation Types'

    def __str__(self):
        return self.disaggregation_type


class DisaggregationLabel(models.Model):
    disaggregation_type = models.ForeignKey(
        DisaggregationType, on_delete=models.CASCADE,
        related_name='disaggregation_label')
    label = models.CharField(max_length=765, blank=True)
    customsort = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('customsort',)
        verbose_name = 'Disaggregation Label'
        verbose_name_plural = 'Disaggregation Labels'

    def __str__(self):
        return self.label


class DisaggregationValue(models.Model):
    disaggregation_label = models.ForeignKey(
        DisaggregationLabel, on_delete=models.CASCADE)
    value = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.value


class ReportingFrequency(models.Model):
    frequency = models.CharField(max_length=135, blank=True)
    description = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('frequency',)
        verbose_name = 'Reporting Frequency'
        verbose_name_plural = 'Reporting Frequencies'

    def __str__(self):
        return self.frequency


class DataCollectionFrequency(models.Model):
    frequency = models.CharField(max_length=135, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    numdays = models.PositiveIntegerField(
        default=0, verbose_name="Frequency in number of days")
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('frequency',)
        verbose_name = 'Data Collection Frequency'
        verbose_name_plural = 'Data Collection Frequencies'

    def __str__(self):
        return self.frequency or ''


class ReportingPeriod(models.Model):
    frequency = models.ForeignKey(
        ReportingFrequency, null=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.frequency


class ExternalService(models.Model):
    name = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=765, blank=True)
    feed_url = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'External Service'
        verbose_name_plural = 'External Services'

    def __str__(self):
        return self.name


class ExternalServiceRecord(models.Model):
    external_service = models.ForeignKey(
        ExternalService, blank=True, null=True, on_delete=models.SET_NULL)
    full_url = models.CharField(max_length=765, blank=True)
    record_id = models.CharField("Unique ID", max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'External Service Record'
        verbose_name_plural = 'External Service Records'

    def __str__(self):
        return self.full_url


class IndicatorManager(models.Manager):
    def get_queryset(self):
        return super(IndicatorManager, self).get_queryset() \
            .prefetch_related('program').select_related('sector')


class Indicator(models.Model):
    LOP = 1
    ANNUAL = 3
    SEMI_ANNUAL = 4
    TRI_ANNUAL = 5
    QUARTERLY = 6
    MONTHLY = 7
    WEEKLY = 8
    BIWEEKLY = 9

    TARGET_FREQUENCIES = (
        (LOP, 'Life of Program only'),
        (ANNUAL, 'Every Year'),
        (SEMI_ANNUAL, 'Every Six Months'),
        (TRI_ANNUAL, 'Every Four Months'),
        (QUARTERLY, 'Every Three Months'),
        (MONTHLY, 'Every Month'),
        (WEEKLY, 'Every Week'),
        (BIWEEKLY, 'Every Two Weeks')
    )

    indicator_key = models.UUIDField(
        default=uuid.uuid4, unique=True, help_text=" "),
    indicator_type = models.ManyToManyField(
        IndicatorType, blank=True, help_text=" ")
    level = models.ManyToManyField(Level, blank=True, help_text=" ")
    objectives = models.ManyToManyField(
        Objective, blank=True, verbose_name="Objective",
        related_name="obj_indicator", help_text=" ")
    strategic_objectives = models.ManyToManyField(
        StrategicObjective, verbose_name="Strategic objective",
        blank=True, related_name="strat_indicator", help_text=" ")
    name = models.CharField(verbose_name="Name",
                            max_length=255, help_text=" ")
    number = models.CharField(
        max_length=255, null=True, blank=True, help_text=" ")
    source = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Data source", help_text=" ")
    definition = models.TextField(null=True, blank=True, help_text=" ")
    justification = models.TextField(
        max_length=500, null=True, blank=True,
        verbose_name="Justification for indicator", help_text=" ")
    unit_of_measure = models.CharField(
        max_length=135, null=True, blank=True, verbose_name="Unit of measure",
        help_text=" ")
    disaggregation = models.ManyToManyField(
        DisaggregationType, blank=True, related_name="indicator_disaggregation_types")
    baseline = models.CharField(
        verbose_name="Baseline", max_length=255, null=True, blank=True,
        help_text=" ")
    baseline_na = models.BooleanField(
        verbose_name="Not applicable", default=False, help_text=" ")
    lop_target = models.CharField(verbose_name="Overall target",
                                  max_length=255, null=True, blank=True,
                                  help_text=" ")
    rationale_for_target = models.TextField(
        max_length=255, null=True, blank=True, help_text=" ")
    target_frequency = models.IntegerField(
        blank=True, null=True, choices=TARGET_FREQUENCIES,
        verbose_name="Target frequency", help_text=" ")
    target_frequency_custom = models.CharField(
        null=True, blank=True, max_length=100,
        verbose_name="First event name*", help_text=" ")
    target_frequency_start = models.DateField(
        blank=True, null=True, auto_now=False, auto_now_add=False,
        verbose_name="First target period begins*", help_text=" ")
    target_frequency_num_periods = models.IntegerField(
        blank=True, null=True, verbose_name="Number of target periods*",
        help_text=" ")
    means_of_verification = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Means of verification", help_text=" ")
    data_collection_method = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Data collection method", help_text=" ")
    data_collection_frequency = models.ForeignKey(
        DataCollectionFrequency, null=True, blank=True,
        verbose_name="Data collection frequency",
        help_text=" ", on_delete=models.SET_NULL)
    data_points = models.TextField(
        max_length=500, null=True, blank=True, verbose_name="Data points",
        help_text=" ")
    responsible_person = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Responsible person or team", help_text=" ")
    method_of_analysis = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Method of analysis", help_text=" ")
    information_use = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Information use",
        help_text=" ")
    reporting_frequency = models.ForeignKey(
        ReportingFrequency, null=True,
        blank=True,
        verbose_name="Reporting frequency",
        help_text=" ",
        on_delete=models.SET_NULL)
    quality_assurance = models.TextField(
        max_length=500, null=True, blank=True,
        verbose_name="Quality assurance measures", help_text=" ")
    data_issues = models.TextField(
        max_length=500, null=True, blank=True, verbose_name="Data issues",
        help_text=" ")
    indicator_changes = models.TextField(
        max_length=500, null=True, blank=True,
        verbose_name="Changes to indicator", help_text=" ")
    comments = models.TextField(
        max_length=255, null=True, blank=True, help_text=" ")
    program = models.ManyToManyField(Program, help_text=" ")
    sector = models.ForeignKey(
        Sector, null=True, blank=True, help_text=" ",
        on_delete=models.SET_NULL)
    key_performance_indicator = models.BooleanField(
        "Key Performance Indicator for this program?", default=False,
        help_text=" ")
    approved_by = models.ForeignKey(ActivityUser, blank=True, null=True,
                                    related_name="approving_indicator",
                                    help_text=" ", on_delete=models.SET_NULL)
    approval_submitted_by = models.ForeignKey(
        ActivityUser, blank=True, null=True,
        related_name="indicator_submitted_by",
        help_text=" ", on_delete=models.SET_NULL)
    external_service_record = models.ForeignKey(
        ExternalServiceRecord, verbose_name="External Service ID", blank=True,
        null=True,
        help_text=" ", on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True, help_text=" ")
    edit_date = models.DateTimeField(null=True, blank=True, help_text=" ")
    history = HistoricalRecords()
    notes = models.TextField(max_length=500, null=True, blank=True)
    # optimize query for class based views etc.
    objects = IndicatorManager()

    class Meta:
        ordering = ('create_date',)

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Indicator, self).save(*args, **kwargs)

    @property
    def is_target_frequency_time_aware(self):
        return self.target_frequency in (self.ANNUAL, self.SEMI_ANNUAL,
                                         self.TRI_ANNUAL, self.QUARTERLY,
                                         self.MONTHLY)

    @property
    def just_created(self):
        if self.create_date >= timezone.now() - timedelta(minutes=5):
            return True
        return False

    @property
    def name_clean(self):
        return self.name.encode('ascii', 'ignore')

    @property
    def objectives_list(self):
        return ', '.join([x.name for x in self.objectives.all()])

    @property
    def strategicobjectives_list(self):
        return ', '.join([x.name for x in self.strategic_objectives.all()])

    @property
    def programs(self):
        return ', '.join([x.name for x in self.program.all()])

    @property
    def indicator_types(self):
        return ', '.join([x.indicator_type for x in self.indicator_type.all()])

    @property
    def levels(self):
        return ', '.join([x.name for x in self.level.all()])

    @property
    def disaggregations(self):
        return ', '.join(
            [x.disaggregation_type for x in self.disaggregation.all()])

    @property
    def get_target_frequency_label(self):
        if self.target_frequency:
            return Indicator.TARGET_FREQUENCIES[self.target_frequency - 1][1]
        return None

    def __str__(self):
        return self.name


class PeriodicTarget(models.Model):
    indicator = models.ForeignKey(
        Indicator, null=False, blank=False, on_delete=models.CASCADE)
    period = models.CharField(max_length=255, null=True, blank=True)
    target = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal('0.00'))
    start_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    customsort = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(
        null=True, blank=True, auto_now_add=True)
    edit_date = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        if self.indicator.target_frequency == Indicator.LOP:
            return self.period
        if self.start_date and self.end_date:
            return "%s (%s - %s)" % (
                self.period, self.start_date.strftime('%b %d, %Y'),
                self.end_date.strftime('%b %d, %Y'))
        return self.period

    class Meta:
        ordering = ('customsort', '-create_date')
        verbose_name = 'Periodic Target'
        verbose_name_plural = 'Periodic Targets'

    @property
    def start_date_formatted(self):
        if self.start_date:
            return self.start_date.strftime('%b %d, %Y').replace(" 0", " ")
        return self.start_date

    @property
    def end_date_formatted(self):
        if self.end_date:
            return self.end_date.strftime('%b %d, %Y').replace(" 0", " ")
        return self.end_date


class CollectedDataManager(models.Manager):
    def get_queryset(self):
        return super(CollectedDataManager,
                     self).get_queryset()\
            .prefetch_related('site', 'disaggregation_value') \
            .select_related('program', 'indicator', 'agreement', 'complete',
                            'evidence', 'activity_table')


class CollectedData(models.Model):
    data_key = models.UUIDField(
        default=uuid.uuid4, unique=True, help_text=" "),
    periodic_target = models.ForeignKey(
        PeriodicTarget, null=True, blank=True, help_text=" ",
        on_delete=models.SET_NULL)
    targeted = models.DecimalField("Targeted", max_digits=20, null=True, blank=True,
                                   decimal_places=2, default=Decimal('0.00'))
    achieved = models.DecimalField(
        "Achieved", max_digits=20, decimal_places=2, blank=True, null=True)
    disaggregation_value = models.ManyToManyField(
        DisaggregationValue, blank=True, help_text=" ")
    description = models.TextField(
        "Remarks/comments", blank=True, null=True, help_text=" ")
    indicator = models.ForeignKey(
        Indicator, help_text=" ", null=True, blank=True, on_delete=models.SET_NULL)
    agreement = models.ForeignKey(ProjectAgreement, blank=True, null=True,
                                  related_name="q_agreement2",
                                  verbose_name="Project Initiation",
                                  help_text=" ", on_delete=models.SET_NULL)
    complete = models.ForeignKey(ProjectComplete, blank=True, null=True,
                                 related_name="q_complete2",
                                 on_delete=models.SET_NULL, help_text=" ")
    program = models.ForeignKey(Program, blank=True, null=True,
                                related_name="i_program", help_text=" ",
                                on_delete=models.SET_NULL)
    date_collected = models.DateTimeField(null=True, blank=True, help_text=" ")
    comment = models.TextField(
        "Comment/Explanation", max_length=255, blank=True, null=True,
        help_text=" ")
    evidence = models.ForeignKey(Documentation, null=True, blank=True,
                                 verbose_name="Evidence Document or Link",
                                 help_text=" ", on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(ActivityUser, blank=True, null=True,
                                    verbose_name="Originated By",
                                    related_name="approving_data",
                                    help_text=" ", on_delete=models.SET_NULL)
    activity_table = models.ForeignKey(
        ActivityTable, blank=True, null=True, help_text=" ",
        on_delete=models.SET_NULL)
    update_count_activity_table = models.BooleanField(
        "Would you like to update the achieved total with the row "
        "count from activitytables?",
        default=False, help_text=" ")
    create_date = models.DateTimeField(null=True, blank=True, help_text=" ")
    edit_date = models.DateTimeField(null=True, blank=True, help_text=" ")
    site = models.ManyToManyField(SiteProfile, blank=True, help_text=" ")
    history = HistoricalRecords()
    objects = CollectedDataManager()

    class Meta:
        ordering = ('agreement', 'indicator', 'date_collected', 'create_date')
        verbose_name_plural = "Collected Data"

    # onsave add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(CollectedData, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.description

    def achieved_sum(self):
        achieved = CollectedData.targeted.filter(
            indicator__id=self).sum('achieved')
        return achieved

    @property
    def date_collected_formatted(self):
        if self.date_collected:
            return self.date_collected.strftime('%b %d, %Y').replace(" 0", " ")
        return self.date_collected

    @property
    def disaggregations(self):
        return ', '.join(
            [y.disaggregation_label.label + ': ' + y.value for y in
             self.disaggregation_value.all()])
