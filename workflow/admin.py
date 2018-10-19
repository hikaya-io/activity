from .models import *
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin, ExportMixin
from tola.util import getCountry
from admin_report.mixins import ChartReportAdmin


# Resource for CSV export
class DocumentationResource(resources.ModelResource):
    country = fields.Field(column_name='country', attribute='country', widget=ForeignKeyWidget(Country, 'country'))
    program = fields.Field(column_name='program', attribute='program', widget=ForeignKeyWidget(Program, 'name'))
    project = fields.Field(column_name='project', attribute='project', widget=ForeignKeyWidget(ProjectAgreement, 'project_name'))

    class Meta:
        model = Documentation
        widgets = {
                'create_date': {'format': '%d/%m/%Y'},
                'edit_date': {'format': '%d/%m/%Y'},
                'expected_start_date': {'format': '%d/%m/%Y'},
                }


class DocumentationAdmin(ImportExportModelAdmin):
    resource_class = DocumentationResource
    list_display = ('program','project')
    list_filter = ('program__country',)
    pass


# Resource for CSV export
class ProjectAgreementResource(resources.ModelResource):

    class Meta:
        model = ProjectAgreement
        widgets = {
                'create_date': {'format': '%d/%m/%Y'},
                'edit_date': {'format': '%d/%m/%Y'},
                'expected_start_date': {'format': '%d/%m/%Y'},
                'expected_end_date': {'format': '%d/%m/%Y'},
                }


class ProjectAgreementAdmin(ImportExportModelAdmin):
    resource_class = ProjectAgreementResource
    list_display = ('program','project_name','short','create_date')
    list_filter = ('program__country','short')
    filter_horizontal = ('capacity','evaluate','site','stakeholder')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Filter by logged in users allowable countries
        user_countries = getCountry(request.user)
        #if not request.user.user.is_superuser:
        return queryset.filter(country__in=user_countries)

    pass


# Resource for CSV export
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


class ProjectCompleteAdmin(ImportExportModelAdmin):
    resource_class = ProjectCompleteResource
    list_display = ('program', 'project_name', 'activity_code','short','create_date')
    list_filter = ('program__country', 'office', 'short')
    display = 'project_name'

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Filter by logged in users allowable countries
        user_countries = getCountry(request.user)
        #if not request.user.user.is_superuser:
        return queryset.filter(country__in=user_countries)

    pass


# Resource for CSV export
class CountryResource(resources.ModelResource):

    class Meta:
        model = Country


class CountryAdmin(ImportExportModelAdmin):
    resource_class = CountryResource
    list_display = ('country','code','organization','create_date', 'edit_date')
    list_filter = ('country','organization__name')


# Resource for CSV export
class SiteProfileResource(resources.ModelResource):
    country = fields.Field(column_name='country', attribute='country', widget=ForeignKeyWidget(Country, 'country'))
    type = fields.Field(column_name='type', attribute='type', widget=ForeignKeyWidget(ProfileType, 'profile'))
    office = fields.Field(column_name='office', attribute='office', widget=ForeignKeyWidget(Office, 'code'))
    district = fields.Field(column_name='admin level 2', attribute='district', widget=ForeignKeyWidget(District, 'name'))
    province = fields.Field(column_name='admin level 1', attribute='province', widget=ForeignKeyWidget(Province, 'name'))
    admin_level_three = fields.Field(column_name='admin level 3', attribute='admin_level_three', widget=ForeignKeyWidget(AdminLevelThree, 'name'))

    class Meta:
        model = SiteProfile
        skip_unchanged = True
        report_skipped = False
        #import_id_fields = ['id']


class SiteProfileAdmin(ImportExportModelAdmin):
    resource_class = SiteProfileResource
    list_display = ('name','office', 'country', 'province','district','admin_level_three','village')
    list_filter = ('country__country',)
    search_fields = ('office__code','country__country')
    pass


class ProgramAdmin(admin.ModelAdmin):
    list_display = ('countries','name','gaitid', 'description','budget_check','funding_status')
    search_fields = ('name','gaitid')
    list_filter = ('funding_status','country','budget_check','funding_status')
    display = 'Program'


class ApprovalAuthorityAdmin(admin.ModelAdmin):
    list_display = ('approval_user','budget_limit','fund','country')
    display = 'Approval Authority'
    search_fields = ('approval_user__user__first_name', 'approval_user__user__last_name', 'country__country')
    list_filter = ('create_date','country')

class StakeholderAdmin(ImportExportModelAdmin):
    list_display = ('name', 'type', 'country', 'approval', 'approved_by', 'filled_by', 'create_date')
    display = 'Stakeholder List'
    list_filter = ('country', 'type')

class TolaUserProxyResource(resources.ModelResource):
    country = fields.Field(column_name='country', attribute='country', widget=ForeignKeyWidget(Country, 'country'))
    user = fields.Field(column_name='user', attribute='user', widget=ForeignKeyWidget(User, 'username'))
    email = fields.Field()

    def dehydrate_email(self, user):
            return '%s' % (user.user.email)

    class Meta:
        model = TolaUserProxy
        fields = ('title', 'name', 'user','country','create_date', 'email' )
        export_order = ('title', 'name', 'user','country','email','create_date')


class ReportTolaUserProxyAdmin(ChartReportAdmin, ExportMixin, admin.ModelAdmin ):

    resource_class = TolaUserProxyResource

    def get_queryset(self, request):

        qs = super(ReportTolaUserProxyAdmin, self).get_queryset(request)
        return qs.filter(user__is_active= True)

    list_display = ('title','name', 'user','email', 'country', 'create_date')
    list_filter = ('country', 'create_date', 'user__is_staff')

    def email(self, data):
        auth_users = User.objects.all()
        for a_user in auth_users:
            if data.user == a_user:
                email = a_user.email
        return email

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(AdminLevelThree, AdminLevelThreeAdmin)
admin.site.register(Village)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Sector)
admin.site.register(ProjectAgreement, ProjectAgreementAdmin)
admin.site.register(ProjectComplete, ProjectCompleteAdmin)
admin.site.register(Documentation,DocumentationAdmin)
admin.site.register(Template)
admin.site.register(SiteProfile, SiteProfileAdmin)
admin.site.register(Capacity)
admin.site.register(Monitor)
admin.site.register(Benchmarks)
admin.site.register(Evaluate)
admin.site.register(ProjectType, ProjectTypeAdmin)
admin.site.register(Budget)
admin.site.register(ProfileType)
admin.site.register(ApprovalAuthority, ApprovalAuthorityAdmin)
admin.site.register(ChecklistItem, ChecklistItemAdmin)
admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(Stakeholder, StakeholderAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(StakeholderType)
admin.site.register(TolaUser,TolaUserAdmin)
admin.site.register(TolaSites,TolaSitesAdmin)
admin.site.register(FormGuidance,FormGuidanceAdmin)
admin.site.register(TolaUserProxy, ReportTolaUserProxyAdmin)
admin.site.register(TolaBookmarks, TolaBookmarksAdmin)
