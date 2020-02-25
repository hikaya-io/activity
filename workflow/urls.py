#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .views import (
    list_workflow_level1, ProgramCreate, add_level2, add_documentation,
    add_stakeholder, delete_stakeholder, ProgramUpdate,
    ProjectDash, ProgramDash, level1_delete, ProjectAgreementList,
    ProjectAgreementUpdate,
    ProjectCompleteBySite, ProjectCompleteDetail, DocumentationListObjects,
    SiteProfileList, SiteProfileCreate, SiteProfileUpdate,
    delete_project_agreement, ProjectAgreementImport, ProjectAgreementDetail,
    SiteProfileReport, IndicatorDataBySite, ProjectCompleteList, ProjectCompleteCreate,
    SiteProfileDelete, ProjectCompleteUpdate, ProjectCompleteDelete, DocumentationList,
    ProjectCompleteImport, DocumentationAgreementList, DocumentationCreate, BenchmarkCreate,
    QuantitativeOutputsCreate, DocumentationDelete, DocumentationAgreementCreate,
    export_stakeholders_list, DocumentationAgreementUpdate, DocumentationUpdate, ChecklistItemList,
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemDelete, ContactList,
    ContactCreate, ContactUpdate, BenchmarkUpdate, BenchmarkDelete, StakeholderList,
    StakeholderObjects, StakeholderCreate, StakeholderUpdate, province_json, service_json,
    save_bookmark, district_json, country_json, export_sites_list, ReportData, DocumentationAgreementDelete,
    QuantitativeOutputsUpdate, QuantitativeOutputsDelete, BudgetList, BudgetCreate,
    BudgetUpdate, BudgetDelete, Report, SiteProfileObjects, checklist_update_link, delete_contact,
    ProfileTypeCreate, ProfileTypeList, ProfileTypeUpdate, ProfileTypeDelete,
    FundCodeList, FundCodeCreate, FundCodeUpdate, FundCodeDelete, OfficeView
)
from django.urls import path, re_path

# place app url patterns here

urlpatterns = [
    # level1
    path('level1', list_workflow_level1, name='level1'),
    path('level1_delete/<int:pk>/', level1_delete, name='level1_delete'),
    path('level1/add', ProgramCreate.as_view(), name='add_level1'),

    path('level2/add', add_level2, name='add-level2'),
    path('documentation/add', add_documentation, name='add-documentation'),
    path('contact/add', ContactCreate.as_view(), name='add-contact'),
    path('stakeholder/add', add_stakeholder, name='add-stakeholder'),
    path('stakeholder/delete_stakeholder/<int:pk>/',
         delete_stakeholder, name='delete_stakeholder'),
    path('level1/edit/<int:pk>/', ProgramUpdate.as_view(), name='level1_edit'),
    path('level2/project/<int:pk>/', ProjectDash.as_view(), name='project_dashboard'),
    path('level2/project/<int:pk>/', ProjectDash.as_view(), name='project_dashboard'),
    path('level2/list/<slug:program>/<slug:status>/', ProgramDash.as_view(),
        name='projects_list'),

    # projects / project agreements
    path('<int:pk>/', ProjectAgreementList.as_view(),
        name='projectagreement_list'),
    path('projectagreement_update/<int:pk>/', ProjectAgreementUpdate.as_view(),
        name='projectagreement_update'),
    path('projectagreement_delete/<int:pk>/', delete_project_agreement,
        name='projectagreement_delete'),
    path('projectagreement_import/', ProjectAgreementImport.as_view(),
        name='projectagreement_import'),
    path('projectagreement_detail/<int:pk>/', ProjectAgreementDetail.as_view(),
        name='projectagreement_detail'),
    path('projectcomplete_list/<int:pk>/', ProjectCompleteList.as_view(),
        name='projectcomplete_list'),
    path('projectcomplete_add/<int:pk>/', ProjectCompleteCreate.as_view(),
        name='projectcomplete_add'),
    path('projectcomplete_update/<int:pk>/', ProjectCompleteUpdate.as_view(),
        name='proejctcomplete_update'),
    path('projectcomplete_delete/<int:pk>/', ProjectCompleteDelete.as_view(),
        name='projectcomplete_delete'),
    path('projectcomplete_import/', ProjectCompleteImport.as_view(),
        name='projectcomplete_import'),
    path('projectcomplete_detail/<int:pk>/', ProjectCompleteDetail.as_view(),
        name='projectcomplete_detail'),

    # site profiles
    path('siteprofile_list/<slug:program_id>/<slug:activity_id>/<slug:display>/',
        SiteProfileList.as_view(), name='siteprofile_list'),
    path('siteprofile_report/<int:pk>/', SiteProfileReport.as_view(),
        name='siteprofile_report'),
    path('siteprofile_add/', SiteProfileCreate.as_view(),
        name='siteprofile_add'),
    path('siteprofile_update/<int:pk>/', SiteProfileUpdate.as_view(),
        name='siteprofile_update'),
    path('siteprofile_delete/<int:pk>/', SiteProfileDelete.as_view(),
        name='siteprofile_delete'),
    path('site_indicatordata/<slug:site_ide>/', IndicatorDataBySite.as_view(),
        name='site_indicatordata'),
    path('site_projectscomplete/<slug:site_id>/', ProjectCompleteBySite.as_view(),
        name='site_projectscomplete'),

    # documentation
    path('documentation_list/<slug:program>/<slug:project>/',
        DocumentationList.as_view(), name='documentation_list'),
    path('documentation_objects/<slug:program>/<slug:project>/',
        DocumentationListObjects.as_view(), name='documentation_objects'),
    path('documentation_add/', DocumentationCreate.as_view(),
        name='documentation_add'),
    path('documentation_agreement_list/<slug:program>/<slug:project>/',
        DocumentationAgreementList.as_view(),
        name='documentation_agreement_list'),
    path('documentation_agreement_add/<int:id>/',
        DocumentationAgreementCreate.as_view(),
        name='documentation_agreement_add'),
    path('documentation_agreement_update/<int:pk>/<int:id>',
        DocumentationAgreementUpdate.as_view(),
        name='documentation_agreement_update'),
    path('documentation_agreement_delete/<int:pk>/',
        DocumentationAgreementDelete.as_view(),
        name='documentation_agreement_delete'),
    path('documentation_update/<int:pk>/', DocumentationUpdate.as_view(),
        name='documentation_update'),
    path('documentation_delete/<int:pk>/', DocumentationDelete.as_view(),
        name='documentation_delete'),

    # quantitative outputs
    path('quantitative_add/<int:id>/', QuantitativeOutputsCreate.as_view(),
        name='quantitative_add'),
    path('quantitative_update/<int:pk>/', QuantitativeOutputsUpdate.as_view(),
        name='quantitative_update'),
    path('quantitative_delete/<int:pk>/', QuantitativeOutputsDelete.as_view(),
        name='quantitative_delete'),

    # benchmarks
    path('benchmark_add/<int:id>/', BenchmarkCreate.as_view(),
        name='benchmark_add'),
    path('benchmark_update/<int:pk>/', BenchmarkUpdate.as_view(),
        name='benchmark_update'),
    path('benchmark_delete/<int:pk>/', BenchmarkDelete.as_view(),
        name='benchmark_delete'),
    path('benchmark_complete_add/<int:id>/', BenchmarkCreate.as_view(),
        name='benchmark_add'),
    path('benchmark_complete_update/<int:pk>/', BenchmarkUpdate.as_view(),
        name='benchmark_update'),
    path('benchmark_complete_delete/<int:pk>/', BenchmarkDelete.as_view(),
        name='benchmark_delete'),

    # stakeholders
    path('stakeholder_list/<slug:program_id>/<slug:project_id>/',
        StakeholderList.as_view(), name='stakeholder_list'),
    path('stakeholder_table/<slug:program_id>/<int:pk>/',
        StakeholderObjects.as_view(), name='stakeholder_table'),
    path('stakeholder_add/<int:id>/', StakeholderCreate.as_view(),
        name='stakeholder_add'),
    path('stakeholder_update/<int:pk>/', StakeholderUpdate.as_view(),
        name='stakeholder_update'),
    path('export_stakeholders_list/<slug:program_id>/',
        export_stakeholders_list, name='export_stakeholders_list'),

    # sites / site profiles
    path('site_list/<slug:program_id>/<int:pk>/', SiteProfileList.as_view(),
        name='site_list'),
    path('site_table/<slug:program_id>/<int:pk>/',
        SiteProfileObjects.as_view(), name='site_table'),
    path('site_add/<int:id>/', SiteProfileCreate.as_view(),
        name='site_add'),
    path('site_update/<int:pk>/', SiteProfileUpdate.as_view(),
        name='site_update'),
    path('site_delete/<int:pk>/', SiteProfileDelete.as_view(),
        name='site_delete'),
    path('export_sites_list/<slug:program_id>/', export_sites_list,
        name='export_sites_list'),

    # contacts
    path('contact_list/<slug:stakeholder_id>/', ContactList.as_view(),
        name='contact_list'),
    path('contact_add/<slug:stakeholder_id>/<int:id>', ContactCreate.as_view(),
        name='contact_add'),
    path('contact_update/<int:pk>/', ContactUpdate.as_view(),
        name='contact_update'),
    path('contact_delete/<int:pk>/', delete_contact, name='contact_delete'),

    # checklist items
    path('checklistitem_list/<int:pk>/', ChecklistItemList.as_view(),
        name='checklistitem_list'),
    path('checklistitem_add/<int:id>/', ChecklistItemCreate.as_view(),
        name='checklistitem_add'),
    path('checklistitem_update/<int:pk>/', ChecklistItemUpdate.as_view(),
        name='checklistitem_update'),
    path('checklist_update_link/<int:pk>/<slug:type>/<slug:value>/',
        checklist_update_link, name='checklist_update_link'),
    path('checklistitem_delete/<int:pk>/', ChecklistItemDelete.as_view(),
        name='checklistitem_delete'),

    # budgets
    path('budget_list/<int:pk>/', BudgetList.as_view(),
        name='budget_list'),
    path('budget_add/<int:id>/', BudgetCreate.as_view(),
        name='budget_add'),
    path('budget_update/<int:pk>/', BudgetUpdate.as_view(),
        name='budget_update'),
    path('budget_delete/<int:pk>/', BudgetDelete.as_view(),
        name='budget_delete'),

    # reports
    path('report/export/', Report.as_view(), name='report'),
    path('report/<int:pk>/<slug:status>/', Report.as_view(), name='report'),
    path('report_table/<int:pk>/<slug:status>/', ReportData.as_view(), name='report_data'),

    # exports
    path('export_stakeholders_list/', export_stakeholders_list, name='export_stakeholders_list'),
    path('export_sites_list/', export_sites_list, name='export_sites_list'),

    # geography level jsons
    path('province/<slug:province>/province_json/', province_json, name='province_json'),
    path('country/<slug:country>/country_json/', country_json, name='country_json'),
    path('district/<slug:district>/district_json/', district_json, name='district_json'),

    # ajax calls
    path('service/<slug:service>/service_json/', service_json, name='service_json'),
    path('new_bookmark/', save_bookmark, name='save_bookmark'),


    # ProfileType Urls
    path(
        'profile_type/add',
        ProfileTypeCreate.as_view(),
        name='profile_type_add'
    ),
    path(
        'profile_type/list',
        ProfileTypeList.as_view(),
        name='profile_type_list'
    ),
    path(
        'profile_type/edit/<int:id>',
        ProfileTypeUpdate.as_view(),
        name='profile_type_edit'
    ),
    path(
        'profile_type/delete/<int:id>',
        ProfileTypeDelete.as_view(),
        name='profile_type_delete'
    ),

    # ProfileType Urls
    path(
        'fund_code/add',
        FundCodeCreate.as_view(),
        name='fund_code_add'
    ),
    path(
        'fund_code/list',
        FundCodeList.as_view(),
        name='fund_code_list'
    ),
    path(
        'fund_code/edit/<int:id>',
        FundCodeUpdate.as_view(),
        name='fund_code_edit'
    ),
    path(
        'fund_code/delete/<int:id>',
        FundCodeDelete.as_view(),
        name='fund_code_delete'
    ),

    #Office Urls
    # path(
    #     'office/add',
    #     OfficeCreate.as_view(),
    #     name='office_add'
    # ),
    # path(
    #     'office/list',
    #     OfficeList.as_view(),
    #     name='office_list'
    # ),
    # path(
    #     'office/edit/<int:id>',
    #     OfficeUpdate.as_view(),
    #     name='office_edit'
    # ),
    # path(
    #     'office/delete/<int:id>',
    #     OfficeDelete.as_view(),
    #     name='office_delete'
    # ),
    # path(
    #     'office/<int:id>',
    #     OfficeView.as_view(),
    #     name='office_list'
    # ),
    re_path(
        r'office/(?P<pk>.*)',
        OfficeView.as_view(),
        name='office_list'
    )
]
