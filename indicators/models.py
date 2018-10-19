from django.db import models
from django.contrib import admin
from workflow.models import Program, Sector, SiteProfile, ProjectAgreement, ProjectComplete, Country, Office, Documentation, TolaUser
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
from simple_history.models import HistoricalRecords
from decimal import Decimal

class TolaTable(models.Model):
    name = models.CharField(max_length=255, blank=True)
    table_id = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')
    remote_owner = models.CharField(max_length=255, blank=True)
    country = models.ManyToManyField(Country, blank=True)
    url = models.CharField(max_length=255, blank=True)
    unique_count = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class TolaTableAdmin(admin.ModelAdmin):
    list_display = ('name','country','owner','url','create_date','edit_date')
    search_fields = ('country','name')
    list_filter = ('country__country',)
    display = 'Tola Table'


class IndicatorType(models.Model):
    indicator_type = models.CharField(max_length=135, blank=True)
    description = models.TextField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.indicator_type


class IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = ('indicator_type','description','create_date','edit_date')
    display = 'Indicator Type'


class StrategicObjective(models.Model):
    name = models.CharField(max_length=135, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    description = models.TextField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('country','name')

    def __unicode__(self):
        return self.name

    def save(self):
        if self.create_date is None:
            self.create_date = datetime.now()
        super(StrategicObjective, self).save()


class StrategicObjectiveAdmin(admin.ModelAdmin):
    list_display = ('country','name')
    search_fields = ('country__country','name')
    list_filter = ('country__country',)
    display = 'Strategic Objectives'


class Objective(models.Model):
    name = models.CharField(max_length=135, blank=True)
    program = models.ForeignKey(Program, null=True, blank=True)
    description = models.TextField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('program','name')

    def __unicode__(self):
        return self.name

    def save(self):
        if self.create_date is None:
            self.create_date = datetime.now()
        super(Objective, self).save()


class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ('program','name')
    search_fields = ('name','program__name')
    list_filter = ('program__country__country',)
    display = 'Objectives'


class Level(models.Model):
    name = models.CharField(max_length=135, blank=True)
    description = models.TextField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self):
        if self.create_date is None:
            self.create_date = datetime.now()
        super(Level, self).save()


class LevelAdmin(admin.ModelAdmin):
    list_display = ('name')
    display = 'Levels'


class DisaggregationType(models.Model):
    disaggregation_type = models.CharField(max_length=135, blank=True)
    description = models.CharField(max_length=765, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    standard = models.BooleanField(default=False, verbose_name="Standard (TolaData Admins Only)")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.disaggregation_type


class DisaggregationTypeAdmin(admin.ModelAdmin):
    list_display = ('disaggregation_type','country','standard','description')
    list_filter = ('country','standard','disaggregation_type')
    display = 'Disaggregation Type'


class DisaggregationLabel(models.Model):
    disaggregation_type = models.ForeignKey(DisaggregationType)
    label = models.CharField(max_length=765, blank=True)
    customsort = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.label


class DisaggregationLabelAdmin(admin.ModelAdmin):
    list_display = ('disaggregation_type', 'customsort', 'label',)
    display = 'Disaggregation Label'
    list_filter = ('disaggregation_type__disaggregation_type',)


class DisaggregationValue(models.Model):
    disaggregation_label = models.ForeignKey(DisaggregationLabel)
    value = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.value


class DisaggregationValueAdmin(admin.ModelAdmin):
    list_display = ('disaggregation_label','value','create_date','edit_date')
    list_filter = ('disaggregation_label__disaggregation_type__disaggregation_type','disaggregation_label')
    display = 'Disaggregation Value'


class ReportingFrequency(models.Model):
    frequency = models.CharField(max_length=135, blank=True)
    description = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.frequency


class DataCollectionFrequency(models.Model):
    frequency = models.CharField(max_length=135, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    numdays = models.PositiveIntegerField(default=0, verbose_name="Frequency in number of days")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.frequency

class DataCollectionFrequencyAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'description', 'create_date', 'edit_date')
    display = 'Data Collection Frequency'


class ReportingPeriod(models.Model):
    frequency = models.ForeignKey(ReportingFrequency)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.frequency


class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ('frequency','create_date','edit_date')
    display = 'Reporting Frequency'


class ExternalService(models.Model):
    name = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=765, blank=True)
    feed_url = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class ExternalServiceAdmin(admin.ModelAdmin):
    list_display = ('name','url','feed_url','create_date','edit_date')
    display = 'External Indicator Data Service'


class ExternalServiceRecord(models.Model):
    external_service = models.ForeignKey(ExternalService, blank=True, null=True)
    full_url = models.CharField(max_length=765, blank=True)
    record_id = models.CharField("Unique ID",max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.full_url


class ExternalServiceRecordAdmin(admin.ModelAdmin):
    list_display = ('external_service','full_url','record_id','create_date','edit_date')
    display = 'Exeternal Indicator Data Service'


class IndicatorManager(models.Manager):
    def get_queryset(self):
        return super(IndicatorManager, self).get_queryset().prefetch_related('program').select_related('sector')


class Indicator(models.Model):
    LOP = 1
    MID_END = 2
    ANNUAL = 3
    SEMI_ANNUAL = 4
    TRI_ANNUAL = 5
    QUARTERLY = 6
    MONTHLY = 7
    EVENT = 8

    TARGET_FREQUENCIES = (
        (LOP, 'Life of Program (LoP) only'),
        (MID_END, 'Midline and endline'),
        (ANNUAL, 'Annual'),
        (SEMI_ANNUAL, 'Semi-annual'),
        (TRI_ANNUAL, 'Tri-annual'),
        (QUARTERLY, 'Quarterly'),
        (MONTHLY, 'Monthly'),
        (EVENT, 'Event')
    )

    indicator_key = models.UUIDField(default=uuid.uuid4, unique=True, help_text=" "),
    indicator_type = models.ManyToManyField(IndicatorType, blank=True, help_text=" ")
    level = models.ManyToManyField(Level, blank=True, help_text=" ")
    objectives = models.ManyToManyField(Objective, blank=True,verbose_name="Program Objective", related_name="obj_indicator", help_text=" ")
    strategic_objectives = models.ManyToManyField(StrategicObjective, verbose_name="Country Strategic Objective", blank=True, related_name="strat_indicator", help_text=" ")
    name = models.CharField(verbose_name="Name", max_length=255, null=False, help_text=" ")
    number = models.CharField(max_length=255, null=True, blank=True, help_text=" ")
    source = models.CharField(max_length=255, null=True, blank=True, help_text=" ")
    definition = models.TextField(null=True, blank=True, help_text=" ")
    justification = models.TextField(max_length=500, null=True, blank=True, verbose_name="Rationale or Justification for Indicator", help_text=" ")
    unit_of_measure = models.CharField(max_length=135, null=True, blank=True, verbose_name="Unit of measure*", help_text=" ")
    disaggregation = models.ManyToManyField(DisaggregationType, blank=True, help_text=" ")
    baseline = models.CharField(verbose_name="Baseline*", max_length=255, null=True, blank=True, help_text=" ")
    baseline_na = models.BooleanField(verbose_name="Not applicable", default=False, help_text=" ")
    lop_target = models.CharField(verbose_name="Life of Program (LoP) target*",max_length=255, null=True, blank=True, help_text=" ")
    rationale_for_target = models.TextField(max_length=255, null=True, blank=True, help_text=" ")
    target_frequency = models.IntegerField(blank=False, null=True, choices=TARGET_FREQUENCIES, verbose_name="Target frequency", help_text=" ")
    target_frequency_custom = models.CharField(null=True, blank=True, max_length=100, verbose_name="First event name*", help_text=" ")
    target_frequency_start = models.DateField(blank=True, null=True, auto_now=False, auto_now_add=False, verbose_name="First target period begins*", help_text=" ")
    target_frequency_num_periods = models.IntegerField(blank=True, null=True, verbose_name="Number of target periods*", help_text=" ")
    means_of_verification = models.CharField(max_length=255, null=True, blank=True, verbose_name="Means of Verification / Data Source", help_text=" ")
    data_collection_method = models.CharField(max_length=255, null=True, blank=True, verbose_name="Data Collection Method", help_text=" ")
    data_collection_frequency = models.ForeignKey(DataCollectionFrequency, null=True, blank=True, verbose_name="Frequency of Data Collection", help_text=" ")
    data_points = models.TextField(max_length=500, null=True, blank=True, verbose_name="Data Points", help_text=" ")
    responsible_person = models.CharField(max_length=255, null=True, blank=True, verbose_name="Responsible Person(s) and Team", help_text=" ")
    method_of_analysis = models.CharField(max_length=255, null=True, blank=True, verbose_name="Method of Analysis", help_text=" ")
    information_use = models.CharField(max_length=255, null=True, blank=True, verbose_name="Information Use", help_text=" ")
    reporting_frequency = models.ForeignKey(ReportingFrequency, null=True, blank=True, verbose_name="Frequency of Reporting", help_text=" ")
    quality_assurance = models.TextField(max_length=500, null=True, blank=True, verbose_name="Quality Assurance Measures", help_text=" ")
    data_issues = models.TextField(max_length=500, null=True, blank=True, verbose_name="Data Issues", help_text=" ")
    indicator_changes = models.TextField(max_length=500, null=True, blank=True, verbose_name="Changes to Indicator", help_text=" ")
    comments = models.TextField(max_length=255, null=True, blank=True, help_text=" ")
    program = models.ManyToManyField(Program, help_text=" ")
    sector = models.ForeignKey(Sector, null=True, blank=True, help_text=" ")
    key_performance_indicator = models.BooleanField("Key Performance Indicator for this program?",default=False, help_text=" ")
    approved_by = models.ForeignKey(TolaUser, blank=True, null=True, related_name="approving_indicator", help_text=" ")
    approval_submitted_by = models.ForeignKey(TolaUser, blank=True, null=True, related_name="indicator_submitted_by", help_text=" ")
    external_service_record = models.ForeignKey(ExternalServiceRecord, verbose_name="External Service ID", blank=True, null=True, help_text=" ")
    create_date = models.DateTimeField(null=True, blank=True, help_text=" ")
    edit_date = models.DateTimeField(null=True, blank=True, help_text=" ")
    history = HistoricalRecords()
    notes = models.TextField(max_length=500, null=True, blank=True)
    #optimize query for class based views etc.
    objects = IndicatorManager()

    class Meta:
        ordering = ('create_date',)

    def save(self, *args, **kwargs):
        #onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Indicator, self).save(*args, **kwargs)

    @property
    def is_target_frequency_time_aware(self):
        return self.target_frequency in (self.ANNUAL, self.SEMI_ANNUAL, self.TRI_ANNUAL, self.QUARTERLY, self.MONTHLY)

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
        return ', '.join([x.disaggregation_type for x in self.disaggregation.all()])

    @property
    def get_target_frequency_label(self):
        if self.target_frequency:
            return Indicator.TARGET_FREQUENCIES[self.target_frequency-1][1]
        return None

    def __unicode__(self):
        return self.name



class PeriodicTarget(models.Model):
    indicator = models.ForeignKey(Indicator, null=False, blank=False)
    period = models.CharField(max_length=255, null=True, blank=True)
    target = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    start_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    customsort = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        if self.indicator.target_frequency == Indicator.LOP \
            or self.indicator.target_frequency == Indicator.EVENT \
            or self.indicator.target_frequency == Indicator.MID_END:
                return self.period
        if self.start_date and self.end_date:
            return "%s (%s - %s)" % (self.period, self.start_date.strftime('%b %d, %Y'), self.end_date.strftime('%b %d, %Y'))
        return self.period

    class Meta:
        ordering = ('customsort', '-create_date')

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


class PeriodicTargetAdmin(admin.ModelAdmin):
    list_display = ('period', 'target', 'customsort',)
    display = 'Indicator Periodic Target'
    list_filter = ('period',)


class CollectedDataManager(models.Manager):
    def get_queryset(self):
        return super(CollectedDataManager, self).get_queryset().prefetch_related('site','disaggregation_value').select_related('program','indicator','agreement','complete','evidence','tola_table')


class CollectedData(models.Model):
    data_key = models.UUIDField(default=uuid.uuid4, unique=True, help_text = " "),
    periodic_target = models.ForeignKey(PeriodicTarget, null=True, blank=True, help_text = " ")
    #targeted = models.DecimalField("Targeted", max_digits=20, decimal_places=2, default=Decimal('0.00'))
    achieved = models.DecimalField("Achieved", max_digits=20, decimal_places=2, help_text = " ")
    disaggregation_value = models.ManyToManyField(DisaggregationValue, blank=True, help_text = " ")
    description = models.TextField("Remarks/comments", blank=True, null=True, help_text = " ")
    indicator = models.ForeignKey(Indicator, help_text = " ")
    agreement = models.ForeignKey(ProjectAgreement, blank=True, null=True, related_name="q_agreement2", verbose_name="Project Initiation", help_text = " ")
    complete = models.ForeignKey(ProjectComplete, blank=True, null=True, related_name="q_complete2",on_delete=models.SET_NULL, help_text = " ")
    program = models.ForeignKey(Program, blank=True, null=True, related_name="i_program", help_text = " ")
    date_collected = models.DateTimeField(null=True, blank=True, help_text = " ")
    comment = models.TextField("Comment/Explanation", max_length=255, blank=True, null=True, help_text = " ")
    evidence = models.ForeignKey(Documentation, null=True, blank=True, verbose_name="Evidence Document or Link", help_text = " ")
    approved_by = models.ForeignKey(TolaUser, blank=True, null=True, verbose_name="Originated By", related_name="approving_data", help_text = " ")
    tola_table = models.ForeignKey(TolaTable, blank=True, null=True, help_text = " ")
    update_count_tola_table = models.BooleanField("Would you like to update the achieved total with the row count from TolaTables?",default=False, help_text = " ")
    create_date = models.DateTimeField(null=True, blank=True, help_text = " ")
    edit_date = models.DateTimeField(null=True, blank=True, help_text = " ")
    site = models.ManyToManyField(SiteProfile, blank=True, help_text = " ")
    history = HistoricalRecords()
    objects = CollectedDataManager()

    class Meta:
        ordering = ('agreement','indicator','date_collected','create_date')
        verbose_name_plural = "Indicator Output/Outcome Collected Data"

    #onsave add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date == None:
            self.create_date = datetime.now()
        self.edit_date = datetime.utcnow()
        super(CollectedData, self).save()

    #displayed in admin templates
    def __unicode__(self):
        return self.description

    def achieved_sum(self):
        achieved=CollectedData.targeted.filter(indicator__id=self).sum('achieved')
        return achieved

    @property
    def date_collected_formatted(self):
        if self.date_collected:
            return self.date_collected.strftime('%b %d, %Y').replace(" 0", " ")
        return self.date_collected

    @property
    def disaggregations(self):
        return ', '.join([y.disaggregation_label.label + ': ' + y.value for y in self.disaggregation_value.all()])


class CollectedDataAdmin(admin.ModelAdmin):
    list_display = ('indicator','date_collected', 'create_date', 'edit_date')
    list_filter = ['indicator__program__country__country']
    display = 'Indicator Output/Outcome Collected Data'
