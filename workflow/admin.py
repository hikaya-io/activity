#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .models import (
    admin, Country, Documentation, ProjectType, ProjectAgreement, Program, Sector,
    Benchmarks, Budget, SiteProfile, Organization, Evaluate, ProfileType, FundCode,
    AdminLevelThree, ActivityUser, ChecklistItem, Stakeholder, StakeholderType,
    Monitor, Currency, ActivityBookmarks, ActivitySites, ActivityUserOrganizationGroup,
    Office, Province, Template, Capacity, ApprovalAuthority, User, LandType,
    FormGuidance, Contact, Checklist, ProjectComplete, District, Village, UserInvite,
)
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin, ExportMixin
from activity.util import get_country
from adminreport.mixins import ChartReportAdmin


# Proxies
class ActivityUserProxy(ActivityUser):
    class Meta:
        verbose_name, verbose_name_plural = u"Report Activity User", \
                                            u"Report Activity Users"
        proxy = True


# Resources for CSV exports
class DocumentationResource(resources.ModelResource):
    country = fields.Field(column_name='country', attribute='country',
                           widget=ForeignKeyWidget(Country, 'country'))
    program = fields.Field(column_name='program', attribute='program',
                           widget=ForeignKeyWidget(Program, 'name'))
    project = fields.Field(column_name='project', attribute='project',
                           widget=ForeignKeyWidget(ProjectAgreement,
                                                   'project_name'))

    class Meta:
        model = Documentation
        widgets = {
            'create_date': {'format': '%d/%m/%Y'},
            'edit_date': {'format': '%d/%m/%Y'},
            'expected_start_date': {'format': '%d/%m/%Y'},
        }


class ProjectAgreementResource(resources.ModelResource):
    class Meta:
        model = ProjectAgreement
        widgets = {
            'create_date': {'format': '%d/%m/%Y'},
            'edit_date': {'format': '%d/%m/%Y'},
            'expected_start_date': {'format': '%d/%m/%Y'},
            'expected_end_date': {'format': '%d/%m/%Y'},
        }


class ProjectCompleteResource(resources.ModelResource):
    class Meta:
        model = ProjectComplete
        widgets = {
            'create_date': {'format': '%d/%m/%Y'},
            'edit_date': {'format': '%d/%m/%Y'},
            'expected_start_date': {'format': '%d/%m/%Y'},
            'expected_end_date': {'format': '%d/%m/%Y'},
            'actual_start_date': {'format': '%d/%m/%Y'},
            'actual_end_date': {'format': '%d/%m/%Y'},
        }


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country


class ActivityUserProxyResource(resources.ModelResource):
    country = fields.Field(column_name='country', attribute='country',
                           widget=ForeignKeyWidget(Country, 'country'))
    user = fields.Field(column_name='user', attribute='user',
                        widget=ForeignKeyWidget(User, 'username'))
    email = fields.Field()

    def dehydrate_email(self, user):
        return str(user.user.email)

    class Meta:
        model = ActivityUserProxy
        fields = ('title', 'name', 'user', 'country', 'create_date', 'email')
        export_order = ('title', 'name', 'user',
                        'country', 'email', 'create_date')


class ReportActivityUserProxyAdmin(ChartReportAdmin, ExportMixin,
                                   admin.ModelAdmin):
    resource_class = ActivityUserProxyResource

    def get_queryset(self, request):

        qs = super(ReportActivityUserProxyAdmin, self).get_queryset(request)
        return qs.filter(user__is_active=True)

    list_display = ('title', 'name', 'user', 'email', 'country', 'create_date')
    list_filter = ('country', 'create_date', 'user__is_staff')

    def email(self, data):
        auth_users = User.objects.all()
        email = ''
        for a_user in auth_users:
            if data.user == a_user:
                email = a_user.email
        return email


class SiteProfileResource(resources.ModelResource):
    country = fields.Field(column_name='country', attribute='country',
                           widget=ForeignKeyWidget(Country, 'country'))
    type = fields.Field(column_name='type', attribute='type',
                        widget=ForeignKeyWidget(ProfileType, 'profile'))
    office = fields.Field(column_name='office', attribute='office',
                          widget=ForeignKeyWidget(Office, 'code'))
    district = fields.Field(column_name='admin level 2',
                            attribute='district',
                            widget=ForeignKeyWidget(District, 'name'))
    province = fields.Field(column_name='admin level 1',
                            attribute='province',
                            widget=ForeignKeyWidget(Province, 'name'))
    admin_level_three = fields.Field(
        column_name='admin level 3', attribute='admin_level_three',
        widget=ForeignKeyWidget(AdminLevelThree, 'name'))

    class Meta:
        model = SiteProfile
        skip_unchanged = True
        report_skipped = False


# Models Registration to the admin site
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Organization'


@admin.register(ActivityUser)
class ActivityUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    display = 'Activity User'
    list_filter = ('country', 'user__is_staff',)
    search_fields = ('name', 'country__country', 'title')


@admin.register(Documentation)
class DocumentationAdmin(ImportExportModelAdmin):
    resource_class = DocumentationResource
    list_display = ('program', 'project')
    list_filter = ('program__country',)


@admin.register(ProjectAgreement)
class ProjectAgreementAdmin(ImportExportModelAdmin):
    resource_class = ProjectAgreementResource
    list_display = ('program', 'project_name', 'short', 'create_date')
    list_filter = ('program__country', 'short')
    filter_horizontal = ('capacity', 'evaluate', 'site', 'stakeholder')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Filter by logged in users allowable countries
        user_countries = get_country(request.user)
        # if not request.user.user.is_superuser:
        return queryset.filter(country__in=user_countries)


@admin.register(ProjectComplete)
class ProjectCompleteAdmin(ImportExportModelAdmin):
    resource_class = ProjectCompleteResource
    list_display = ('program', 'project_name',
                    'activity_code', 'short', 'create_date')
    list_filter = ('program__country', 'office', 'short')
    display = 'project_name'

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Filter by logged in users allowable countries
        user_countries = get_country(request.user)
        # if not request.user.user.is_superuser:
        return queryset.filter(country__in=user_countries)


@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    resource_class = CountryResource
    list_display = ('country', 'code', 'organization',
                    'create_date', 'edit_date')
    list_filter = ('country', 'organization__name')


@admin.register(SiteProfile)
class SiteProfileAdmin(ImportExportModelAdmin):
    resource_class = SiteProfileResource
    list_display = ('name', 'office', 'country', 'province',
                    'district', 'admin_level_three', 'village')
    list_filter = ('country__country',)
    search_fields = ('office__code', 'country__country')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'program_uuid', 'name', 'start_date', 'end_date')
    search_fields = ('name', 'program_uuid')
    list_filter = ('funding_status', 'country', 'program_uuid', 'start_date')
    display = 'Program'


@admin.register(ApprovalAuthority)
class ApprovalAuthorityAdmin(admin.ModelAdmin):
    list_display = ('approval_user', 'budget_limit', 'fund', 'country')
    display = 'Approval Authority'
    search_fields = ('approval_user__user__first_name',
                     'approval_user__user__last_name', 'country__country')
    list_filter = ('create_date', 'country')


@admin.register(Stakeholder)
class StakeholderAdmin(ImportExportModelAdmin):
    list_display = ('name', 'type', 'country', 'approval',
                    'approved_by', 'filled_by', 'create_date')
    display = 'Stakeholder List'
    list_filter = ('country', 'type')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'code')
    list_filter = ('name', 'code')


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = ('invite_uuid', 'email', 'organization', 'status', 'invite_date')
    list_filter = ('organization', 'status')


@admin.register(ActivityUserOrganizationGroup)
class ActivityUserOrganizationGroupAdmin(admin.ModelAdmin):
    list_display = ('activity_user', 'organization', 'create_date', 'edit_date')
    list_filter = ('activity_user', 'organization')


@admin.register(FundCode)
class FundCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'stakeholder__name', 'create_date', 'edit_date')
    display = 'Fund Code'


@admin.register(Evaluate)
class EvaluateAdmin(admin.ModelAdmin):
    list_display = ('evaluate', 'create_date', 'edit_date')
    display = 'Evaluate'


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'create_date', 'edit_date')
    display = 'Project Type'


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'documentation_type',
                    'file_field', 'create_date', 'edit_date')
    display = 'Template'


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ('responsible_person', 'frequency',
                    'type', 'create_date', 'edit_date')
    display = 'Monitor'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'description_of_contribution',
                    'proposed_value', 'create_date', 'edit_date')
    display = 'Budget'


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country', 'agreement')


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'checklist', 'in_file')
    list_filter = ('checklist', 'global_item')


@admin.register(ActivitySites)
class ActivitySitesAdmin(admin.ModelAdmin):
    list_display = ('name', 'agency_name')
    display = 'Activity Site'
    list_filter = ('name',)
    search_fields = ('name', 'agency_name')


@admin.register(FormGuidance)
class FormGuidanceAdmin(admin.ModelAdmin):
    list_display = ('form', 'guidance', 'guidance_link', 'create_date',)
    display = 'Form Guidance'


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('sector', 'create_date', 'edit_date')
    display = 'Sector'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'create_date', 'edit_date')
    display = 'Contact'
    list_filter = ('create_date', 'country')
    search_fields = ('name', 'country', 'title', 'city')


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'province', 'create_date', 'edit_date')
    search_fields = ('name', 'province__name', 'code')
    list_filter = ('create_date', 'province__country__country')
    display = 'Office'


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'create_date')
    search_fields = ('name', 'country__country')
    list_filter = ('create_date', 'country')
    display = 'Admin Level 1'


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'create_date')
    search_fields = ('create_date', 'province')
    list_filter = ('province__country__country', 'province')
    display = 'Admin Level 2'


@admin.register(AdminLevelThree)
class AdminLevelThreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'create_date')
    search_fields = ('name', 'district__name')
    list_filter = ('district__province__country__country', 'district')
    display = 'Admin Level 3'


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'create_date', 'edit_date')
    list_filter = ('district__province__country__country', 'district')
    display = 'Admin Level 4'


@admin.register(ProfileType)
class ProfileTypeAdmin(admin.ModelAdmin):
    list_display = ('profile', 'create_date', 'edit_date')
    display = 'ProfileType'


@admin.register(LandType)
class LandTypeAdmin(admin.ModelAdmin):
    list_display = ('classify_land', 'create_date', 'edit_date')
    display = 'Land Type'


@admin.register(Capacity)
class CapacityAdmin(admin.ModelAdmin):
    list_display = ('capacity', 'create_date', 'edit_date')
    display = 'Capacity'


@admin.register(StakeholderType)
class StakeholderTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Stakeholder Types'
    list_filter = 'create_date'
    search_fields = 'name'


@admin.register(Benchmarks)
class BenchmarksAdmin(admin.ModelAdmin):
    list_display = ('description', 'agreement__name',
                    'create_date', 'edit_date')
    display = 'Project Components'


@admin.register(ActivityBookmarks)
class ActivityBookmarksAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')
    display = 'Activity User Bookmarks'
    list_filter = ('user__name',)
    search_fields = ('name', 'user')


# Other Admin site registrations
admin.site.register(ActivityUserProxy, ReportActivityUserProxyAdmin)
