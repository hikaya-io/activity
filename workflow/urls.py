from .views import *

from django.conf.urls import *

# place app url patterns here

urlpatterns = [
                       url(r'^dashboard/project/(?P<pk>\w+)/$', ProjectDash.as_view(), name='project_dashboard'),
                       url(r'^dashboard/project/(?P<pk>\w+)$', ProjectDash.as_view(), name='project_dashboard'),
                       url(r'^dashboard/project', ProjectDash.as_view(), name='project_dashboard'),
                       url(r'^dashboard/(?P<pk>\w+)/(?P<status>[\w ]+)/$', ProgramDash.as_view(), name='dashboard'),
                       url(r'^dashboard/(?P<pk>\w+)/$', ProgramDash.as_view(), name='dashboard'),

                       url(r'^projectagreement_list/(?P<pk>\w+)/(?P<status>[\w ]+)/$', ProjectAgreementList.as_view(), name='projectagreement_list'),
                       url(r'^projectagreement_add/$', ProjectAgreementCreate.as_view(), name='projectagreement_add'),
                       url(r'^projectagreement_update/(?P<pk>\w+)/$', ProjectAgreementUpdate.as_view(), name='projectagreement_update'),
                       url(r'^projectagreement_delete/(?P<pk>\w+)/$', ProjectAgreementDelete.as_view(), name='projectagreement_delete'),
                       url(r'^projectagreement_import', ProjectAgreementImport.as_view(), name='projectagreement_import'),
                       url(r'^projectagreement_detail/(?P<pk>\w+)/$', ProjectAgreementDetail.as_view(), name='projectagreement_detail'),

                       url(r'^projectcomplete_list/(?P<pk>\w+)/$', ProjectCompleteList.as_view(), name='projectcomplete_list'),
                       url(r'^projectcomplete_add/(?P<pk>\w+)/$', ProjectCompleteCreate.as_view(), name='projectcomplete_add'),
                       url(r'^projectcomplete_update/(?P<pk>\w+)/$', ProjectCompleteUpdate.as_view(), name='projectcomplete_update'),
                       url(r'^projectcomplete_delete/(?P<pk>\w+)/$', ProjectCompleteDelete.as_view(), name='projectcomplete_delete'),
                       url(r'^projectcomplete_import', ProjectCompleteImport.as_view(), name='projectcomplete_import'),
                       url(r'^projectcomplete_detail/(?P<pk>\w+)/$', ProjectCompleteDetail.as_view(), name='projectcomplete_detail'),

                       url(r'^siteprofile_list/(?P<program_id>\w+)/(?P<activity_id>\w+)/$', SiteProfileList.as_view(), name='siteprofile_list'),
                       url(r'^siteprofile_report/(?P<pk>\w+)/$', SiteProfileReport.as_view(), name='siteprofile_report'),
                       url(r'^siteprofile_add', SiteProfileCreate.as_view(), name='siteprofile_add'),
                       url(r'^siteprofile_update/(?P<pk>\w+)/$', SiteProfileUpdate.as_view(), name='siteprofile_update'),
                       url(r'^siteprofile_delete/(?P<pk>\w+)/$', SiteProfileDelete.as_view(), name='siteprofile_delete'),

                       url(r'^site_indicatordata/(?P<site_id>\w+)/$', IndicatorDataBySite.as_view(), name='site_indicatordata'),
                       url(r'^site_projectscomplete/(?P<site_id>\w+)/$', ProjectCompleteBySite.as_view(), name='site_projectscomplete'),
                       #url(r'^site_projects/(?P<site_id\w+)/$', ProjectsBySite.as_view(), name='site_projects'),

                       url(r'^documentation_list/(?P<program>\w+)/(?P<project>\w+)/$', DocumentationList.as_view(), name='documentation_list'),
                       url(r'^documentation_objects/(?P<program>\w+)/(?P<project>\w+)/$', DocumentationListObjects.as_view(), name='documentation_objects'),
                       url(r'^documentation_add', DocumentationCreate.as_view(), name='documentation_add'),
                       url(r'^documentation_agreement_list/(?P<program>\w+)/(?P<project>\w+)/$', DocumentationAgreementList.as_view(), name='documentation_agreement_list'),
                       url(r'^documentation_agreement_add/(?P<id>\w+)/$', DocumentationAgreementCreate.as_view(),name='documentation_agreement_add'),
                       url(r'^documentation_agreement_update/(?P<pk>\w+)/(?P<id>\w+)/$', DocumentationAgreementUpdate.as_view(), name='documentation_agreement_update'),
                       url(r'^documentation_agreement_delete/(?P<pk>\w+)/$', DocumentationAgreementDelete.as_view(), name='documentation_agreement_delete'),
                       url(r'^documentation_update/(?P<pk>\w+)/$', DocumentationUpdate.as_view(), name='documentation_update'),
                       url(r'^documentation_delete/(?P<pk>\w+)/$', DocumentationDelete.as_view(), name='documentation_delete'),

                       url(r'^monitor_list/(?P<pk>\w+)/$', MonitorList.as_view(), name='monitor_list'),
                       url(r'^monitor_add/(?P<id>\w+)/$', MonitorCreate.as_view(), name='monitor_add'),
                       url(r'^monitor_update/(?P<pk>\w+)/$', MonitorUpdate.as_view(), name='monitor_update'),
                       url(r'^monitor_delete/(?P<pk>\w+)/$', MonitorDelete.as_view(), name='monitor_delete'),

                       url(r'^quantitative_add/(?P<id>\w+)/$', QuantitativeOutputsCreate.as_view(), name='quantitative_add'),
                       url(r'^quantitative_update/(?P<pk>\w+)/$', QuantitativeOutputsUpdate.as_view(), name='quantitative_update'),
                       url(r'^quantitative_delete/(?P<pk>\w+)/$', QuantitativeOutputsDelete.as_view(), name='quantitative_delete'),

                       url(r'^benchmark_add/(?P<id>\w+)/$', BenchmarkCreate.as_view(), name='benchmark_add'),
                       url(r'^benchmark_update/(?P<pk>\w+)/$', BenchmarkUpdate.as_view(), name='benchmark_update'),
                       url(r'^benchmark_delete/(?P<pk>\w+)/$', BenchmarkDelete.as_view(), name='benchmark_delete'),

                       # urls for projectcomplete version of popup
                       url(r'^benchmark_complete_add/(?P<id>\w+)/$', BenchmarkCreate.as_view(), name='benchmark_add'),
                       url(r'^benchmark_complete_update/(?P<pk>\w+)/$', BenchmarkUpdate.as_view(), name='benchmark_update'),
                       url(r'^benchmark_complete_delete/(?P<pk>\w+)/$', BenchmarkDelete.as_view(), name='benchmark_delete'),

                       url(r'^stakeholder_list/(?P<program_id>\w+)/(?P<pk>\w+)/$', StakeholderList.as_view(), name='stakeholder_list'),

                       url(r'^stakeholder_table/(?P<program_id>\w+)/(?P<pk>\w+)/$', StakeholderObjects.as_view(), name='stakeholder_table'),

                       url(r'^stakeholder_add/(?P<id>\w+)/$', StakeholderCreate.as_view(), name='stakeholder_add'),
                       url(r'^stakeholder_update/(?P<pk>\w+)/$', StakeholderUpdate.as_view(), name='stakeholder_update'),
                       url(r'^stakeholder_delete/(?P<pk>\w+)/$', StakeholderDelete.as_view(), name='stakeholder_delete'),
                       url(r'^export_stakeholders_list/(?P<program_id>\w+)/$', export_stakeholders_list, name='export_stakeholders_list'),

                       url(r'^site_list/(?P<program_id>\w+)/(?P<pk>\w+)/$', SiteProfileList.as_view(), name='site_list'),

                       url(r'^site_table/(?P<program_id>\w+)/(?P<pk>\w+)/$', SiteProfileObjects.as_view(), name='site_table'),

                       url(r'^site_add/(?P<id>\w+)/$', SiteProfileCreate.as_view(), name='site_add'),
                       url(r'^site_update/(?P<pk>\w+)/$', SiteProfileUpdate.as_view(), name='site_update'),
                       url(r'^site_delete/(?P<pk>\w+)/$', SiteProfileDelete.as_view(), name='site_delete'),
                       url(r'^export_sites_list/(?P<program_id>\w+)/$', export_sites_list, name='export_sites_list'),

                       url(r'^contact_list/(?P<pk>\w+)/$', ContactList.as_view(), name='contact_list'),
                       url(r'^contact_add/(?P<stakeholder_id>\w+)/(?P<id>\w+)/$', ContactCreate.as_view(), name='contact_add'),
                       url(r'^contact_update/(?P<stakeholder_id>\w+)/(?P<pk>\w+)/$', ContactUpdate.as_view(), name='contact_update'),
                       url(r'^contact_delete/(?P<pk>\w+)/$', ContactDelete.as_view(), name='contact_delete'),

                       url(r'^checklistitem_list/(?P<pk>\w+)/$', ChecklistItemList.as_view(), name='checklistitem_list'),
                       url(r'^checklistitem_add/(?P<id>\w+)/$', ChecklistItemCreate.as_view(), name='checklistitem_add'),
                       url(r'^checklistitem_update/(?P<pk>\w+)/$', ChecklistItemUpdate.as_view(), name='checklistitem_update'),
                       url(r'^checklist_update_link/(?P<pk>\w+)/(?P<type>\w+)/(?P<value>\w+)/$', checklist_update_link, name='checklist_update_link'),
                       url(r'^checklistitem_delete/(?P<pk>\w+)/$', ChecklistItemDelete.as_view(), name='checklistitem_delete'),

                       url(r'^budget_list/(?P<pk>\w+)/$', BudgetList.as_view(), name='budget_list'),
                       url(r'^budget_add/(?P<id>\w+)/$', BudgetCreate.as_view(), name='budget_add'),
                       url(r'^budget_update/(?P<pk>\w+)/$', BudgetUpdate.as_view(), name='budget_update'),
                       url(r'^budget_delete/(?P<pk>\w+)/$', BudgetDelete.as_view(), name='budget_delete'),

                       url(r'^report/export/$', Report.as_view(), name='report'),
                       url(r'^report/(?P<pk>\w+)/(?P<status>[\w ]+)/$', Report.as_view(), name='report'),
                       url(r'^report_table/(?P<pk>\w+)/(?P<status>[\w ]+)/$', ReportData.as_view(), name='report_data'),
                       url(r'^export_stakeholders_list/', export_stakeholders_list, name='export_stakeholders_list'),
                       url(r'^export_sites_list/', export_sites_list, name='export_sites_list'),

                       url(r'^province/(?P<province>[-\w]+)/province_json/', province_json, name='province_json'),
                       url(r'^country/(?P<country>[-\w]+)/country_json/', country_json, name='country_json'),
                       url(r'^district/(?P<district>[-\w]+)/district_json/', district_json, name='district_json'),

                       #ajax calls
                       url(r'^service/(?P<service>[-\w]+)/service_json/', service_json, name='service_json'),
                       url(r'^new_bookmark/$', save_bookmark, name='save_bookmark'),

]
