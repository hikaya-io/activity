#!/usr/bin/python3
# -*- coding: utf-8 -*-

import operator
import unicodedata
from functools import reduce

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import (
    Program, Country, Province, AdminLevelThree, District, ProjectAgreement,
    ProjectComplete, SiteProfile, Documentation, Monitor, Benchmarks, Budget,
    ApprovalAuthority, Checklist, ChecklistItem, Contact, Stakeholder,
    FormGuidance, StakeholderType,
    ActivityBookmarks, ActivityUser, Sector
)
from formlibrary.models import TrainingAttendance, Distribution
from indicators.models import CollectedData, ExternalService, StrategicObjective
from django.utils import timezone

from .forms import (
    ProjectAgreementForm, ProjectAgreementSimpleForm,
    ProjectAgreementCreateForm,
    ProjectCompleteForm, ProjectCompleteSimpleForm, ProjectCompleteCreateForm,
    DocumentationForm, SiteProfileForm, MonitorForm, BenchmarkForm, BudgetForm,
    FilterForm, ProgramForm,
    QuantitativeOutputsForm, ChecklistItemForm, StakeholderForm, ContactForm
)

import pytz

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q
from .tables import ProjectAgreementTable
from .filters import ProjectAgreementFilter
import json
import requests
import logging

from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.detail import View

from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from activity.util import get_country, email_group, group_excluded, \
    group_required, get_organizations
from .mixins import AjaxableResponseMixin
from .export import ProjectAgreementResource, StakeholderResource, \
    SiteProfileResource
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
# Get an instance of a logger
logger = logging.getLogger(__name__)

APPROVALS = (
    ('in_progress', 'In Progress'),
    ('awaiting_approval', 'Awaiting Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('new', 'New'),
)


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def list_workflow_level1(request):
    user = ActivityUser.objects.filter(user=request.user).first()
    programs = Program.objects.filter(organization=user.organization)
    get_all_sectors = Sector.objects.all()

    context = {'programs': programs,
               'get_all_sectors': get_all_sectors, 'active': ['workflow']}

    return render(request, 'workflow/level1.html', context)


def level1_delete(request, pk):
    """
    Delete program
    :param pk:
    :return:
    """
    program = Program.objects.get(pk=int(pk))
    program.delete()
    return redirect('/workflow/level1')


class ProgramUpdate(UpdateView):
    model = Program
    # fields = '__all__'
    template_name_suffix = '_update_form'
    success_url = '/workflow/level1'
    form_class = ProgramForm

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProgramUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProgramUpdate, self).get_context_data(**kwargs)
        context['current_program'] = self.get_object()
        return context


class ProjectDash(ListView):
    template_name = 'workflow/projectdashboard_list.html'

    def get(self, request, *args, **kwargs):

        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded",
            organization=request.user.activity_user.organization)
        project_id = int(self.kwargs['pk'])

        if project_id == 0:
            get_agreement = None
            get_complete = None
            get_checklist = None
            get_document_count = 0
            get_community_count = 0
            get_training_count = 0
            get_distribution_count = 0
            get_checklist_count = 0
        else:
            get_agreement = ProjectAgreement.objects.get(id=project_id)
            try:
                get_complete = ProjectComplete.objects.get(
                    project_agreement__id=self.kwargs['pk'])
            except ProjectComplete.DoesNotExist:
                get_complete = None
            get_document_count = Documentation.objects.all().filter(
                project_id=self.kwargs['pk']).count()
            get_community_count = SiteProfile.objects.all().filter(
                projectagreement__id=self.kwargs['pk']).count()
            get_training_count = TrainingAttendance.objects.all().filter(
                project_agreement_id=self.kwargs['pk']).count()
            get_distribution_count = Distribution.objects.all().filter(
                initiation_id=self.kwargs['pk']).count()
            get_checklist_count = ChecklistItem.objects.all().filter(
                checklist__agreement_id=self.kwargs['pk']).count()
            get_checklist = ChecklistItem.objects.all().filter(
                checklist__agreement_id=self.kwargs['pk'])

        if int(self.kwargs['pk']) == 0:
            get_program = Program.objects.all().filter(
                funding_status="Funded", country__in=countries).distinct()
        else:
            get_program = Program.objects.get(agreement__id=self.kwargs['pk'])

        return render(request, self.template_name,
                      {'get_program': get_program,
                       'get_agreement': get_agreement,
                       'get_complete': get_complete,
                       'get_programs': get_programs,
                       'get_document_count': get_document_count,
                       'get_checklist_count': get_checklist_count,
                       'get_community_count': get_community_count,
                       'get_training_count': get_training_count,
                       'project_id': project_id,
                       'get_checklist': get_checklist,
                       'get_distribution_count': get_distribution_count})


class ProgramDash(ListView):
    """
    Dashboard links for and status for each program with number of projects
    :param request:
    :param pk: program_id
    :param status: approval status of project
    :return:
    """
    template_name = 'workflow/projectdashboard_list.html'

    def get(self, request, *args, **kwargs):

        get_programs = Program.objects.all().filter(
            organization=request.user.activity_user.organization).distinct()
        filtered_program = None
        status = None
        if int(self.kwargs['program']) == 0:
            get_projects = ProjectAgreement.objects.filter(
                program__organization=request.user.activity_user.organization)
        else:
            filtered_program = Program.objects.get(pk=self.kwargs['program'])

            get_projects = ProjectAgreement.objects.filter(
                program__organization=request.user.activity_user.organization,
                program__id=self.kwargs['program'])

        if self.kwargs.get('status', None):
            status = self.kwargs['status']
            if status != 'none':
                if status == 'in_progress':
                    get_projects = get_projects.filter(
                        Q(approval=self.kwargs['status']) |
                        Q(approval=None))

                elif status == 'new':

                    get_projects = get_projects.filter(
                        Q(approval='') | Q(approval=None))

                else:
                    get_projects = get_projects.filter(approval=status)
                    print('console.log', status)

        return render(request, self.template_name,
                      {
                          'get_programs': get_programs,
                          'APPROVALS': APPROVALS,
                          'get_projects': get_projects,
                          'status': status,
                          'filtered_program': filtered_program,
                          'active': ['workflow'],
                      })


class ProjectAgreementList(ListView):
    """
    Project Agreement
    :param request:
    """
    model = ProjectAgreement
    template_name = 'workflow/projectagreement_list.html'

    def get(self, request, *args, **kwargs):
        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded", country__in=countries).distinct()

        if int(self.kwargs['pk']) != 0:
            get_dashboard = ProjectAgreement.objects.all().filter(
                program__id=self.kwargs['pk'])
            get_program = Program.objects.get(id=self.kwargs['pk'])
            return render(request, self.template_name,
                          {'form': FilterForm(), 'get_program': get_program,
                           'get_dashboard': get_dashboard,
                           'get_programs': get_programs,
                           'APPROVALS': APPROVALS})

        elif self.kwargs['status'] != 'none':
            get_dashboard = ProjectAgreement.objects.all().filter(
                approval=self.kwargs['status'])
            return render(request, self.template_name,
                          {'form': FilterForm(),
                           'get_dashboard': get_dashboard,
                           'get_programs': get_programs,
                           'APPROVALS': APPROVALS})

        else:
            get_dashboard = ProjectAgreement.objects.all().filter(
                program__country__in=countries)

            return render(request, self.template_name,
                          {'form': FilterForm(),
                           'get_dashboard': get_dashboard,
                           'get_programs': get_programs,
                           'APPROVALS': APPROVALS})


class ProjectAgreementImport(ListView):
    """
    Import a project agreement from Hikaya or other third party service
    """

    template_name = 'workflow/projectagreement_import.html'

    def get(self, request, *args, **kwargs):
        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded", country__in=countries)
        get_services = ExternalService.objects.all()
        get_countries = Country.objects.all().filter(country__in=countries)

        return render(request, self.template_name,
                      {'get_programs': get_programs,
                       'get_services': get_services,
                       'get_countries': get_countries})


class ProjectAgreementCreate(CreateView):
    """
    Project Agreement Form
    :param request:
    :param id:
    This is only used in case of an error incomplete form submission fro
    m the simple form in the project dashboard
    """

    model = ProjectAgreement
    template_name = 'workflow/projectagreement_form.html'
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Agreement")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectAgreementCreate, self) \
            .dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProjectAgreementCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    # get shared data from project agreement and pre-populate form with it
    def get_initial(self):

        initial = {
            'approved_by': self.request.user,
            'estimated_by': self.request.user,
            'checked_by': self.request.user,
            'reviewed_by': self.request.user,
            'approval_submitted_by': self.request.user,
        }

        return initial

    def get_context_data(self, **kwargs):
        context = super(ProjectAgreementCreate,
                        self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        # save formset from context
        context = self.get_context_data()

        latest = ProjectAgreement.objects.latest('id')
        get_agreement = ProjectAgreement.objects.get(id=latest.id)

        # create a new dashbaord entry for the project
        get_program = Program.objects.get(id=latest.program_id)

        create_checklist = Checklist(agreement=get_agreement)
        create_checklist.save()

        get_checklist = Checklist.objects.get(id=create_checklist.id)
        get_globals = ChecklistItem.objects.all().filter(global_item=True)
        for item in get_globals:
            ChecklistItem.objects.create(
                checklist=get_checklist, item=item.item)

        messages.success(self.request, 'Success, Initiation Created!')

        redirect_url = '/workflow/dashboard/project/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = ProjectAgreementCreateForm


class ProjectAgreementUpdate(UpdateView):
    """
    Project Initiation Form
    :param request:
    :param id: project_agreement_id
    """
    model = ProjectAgreement
    form_class = ProjectAgreementForm
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Agreement")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectAgreementUpdate, self).dispatch(request, *args,
                                                            **kwargs)

    def get_form(self, form_class=None):
        check_form_type = ProjectAgreement.objects.get(id=self.kwargs['pk'])

        if check_form_type.short:
            form_class = ProjectAgreementSimpleForm
        else:
            form_class = ProjectAgreementForm

        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(ProjectAgreementUpdate,
                        self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})
        context.update({'program': pk})
        get_agreement = ProjectAgreement.objects.get(id=self.kwargs['pk'])
        context.update({'p_agreement': get_agreement.project_name})
        context.update({'p_agreement_program': get_agreement.program})

        try:
            get_quantitative = CollectedData.objects.all().filter(
                agreement__id=self.kwargs['pk']).order_by('indicator')
        except CollectedData.DoesNotExist:
            get_quantitative = None
        context.update({'get_quantitative': get_quantitative})

        try:
            get_monitor = Monitor.objects.all().filter(
                agreement__id=self.kwargs['pk']).order_by('type')
        except Monitor.DoesNotExist:
            get_monitor = None
        context.update({'get_monitor': get_monitor})

        try:
            get_benchmark = Benchmarks.objects.all().filter(
                agreement__id=self.kwargs['pk']).order_by('description')
        except Benchmarks.DoesNotExist:
            get_benchmark = None
        context.update({'get_benchmark': get_benchmark})

        try:
            get_budget = Budget.objects.all().filter(
                agreement__id=self.kwargs['pk']) \
                .order_by('description_of_contribution')
        except Budget.DoesNotExist:
            get_budget = None
        context.update({'get_budget': get_budget})

        try:
            get_documents = Documentation.objects.all().filter(
                project__id=self.kwargs['pk']).order_by('name')
        except Documentation.DoesNotExist:
            get_documents = None
        context.update({'get_documents': get_documents})

        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProjectAgreementUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        # get the approval status of the form before it was submitted and
        # set vars for use in condtions
        check_agreement_status = ProjectAgreement.objects.get(
            id=str(self.kwargs['pk']))
        is_approved = str(form.instance.approval)
        get_program = Program.objects.get(
            agreement__id=check_agreement_status.id)
        country = get_program.country

        # convert form field unicode project name to ascii safe string
        # for email content

        project_name = unicodedata.normalize(
            'NFKD', form.instance.project_name).encode('ascii', 'ignore')
        # check to see if the approval status has changed
        if str(
                is_approved) == "approved" and \
                check_agreement_status.approval != "approved":
            budget = form.instance.total_estimated_budget
            if get_program.budget_check:
                try:
                    user_budget_approval = ApprovalAuthority.objects.get(
                        approval_user__user=self.request.user)
                except ApprovalAuthority.DoesNotExist:
                    user_budget_approval = None
            # compare budget amount to users approval amounts

            if get_program.budget_check:
                if not user_budget_approval or int(budget) > int(
                        user_budget_approval.budget_limit):
                    messages.success(
                        self.request,
                        'You do not appear to have permissions to '
                        'approve this initiation')
                    form.instance.approval = 'awaiting approval'
                else:
                    messages.success(
                        self.request,
                        'Success, Initiation and Budget Approved')
                    form.instance.approval = 'approved'
            else:
                messages.success(self.request, 'Success, Initiation Approved')
                form.instance.approval = 'approved'

            if form.instance.approval == 'approved':
                # email the approver group so they know this was approved
                link = "Link: " + "https://" + get_current_site(
                    self.request).name + "/workflow/projectagreement_detail/" \
                    + str(self.kwargs['pk']) + "/"
                subject = "Project Initiation Approved: " + project_name
                message = "A new initiation was approved by " + \
                          str(self.request.user) + "\n" + "Budget Amount: " \
                          + str(form.instance.total_estimated_budget) + "\n"
                get_submiter = User.objects.get(username=self.request.user)
                email_group(submiter=get_submiter.email, country=country,
                            group=form.instance.approved_by, link=link,
                            subject=subject, message=message)
        elif str(
                is_approved) == "awaiting approval" and \
                check_agreement_status.approval != "awaiting approval":
            messages.success(
                self.request,
                'Success, Initiation has been saved and is now Awaiting '
                'Approval (Notifications have been Sent)')
            # email the approver group so they know this was approved
            link = "Link: " + "https://" + get_current_site(
                self.request).name + "/workflow/projectagreement_detail/" + str(
                self.kwargs['pk']) + "/"
            subject = "Project Initiation Waiting for Approval: " + \
                      project_name
            message = "A new initiation was submitted for approval by " + \
                      str(self.request.user) + "\n" + "Budget Amount: " + \
                      str(form.instance.total_estimated_budget) + "\n"
            email_group(country=country, group=form.instance.approved_by,
                        link=link, subject=subject, message=message)
        else:
            messages.success(self.request, 'Success, form updated!')
        form.save()
        # Not in Use
        # save formset from context
        # context = self.get_context_data()
        self.object = form.save()

        return self.render_to_response(self.get_context_data(form=form))


class ProjectAgreementDetail(DetailView):
    model = ProjectAgreement
    context_object_name = 'agreement'
    queryset = ProjectAgreement.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProjectAgreementDetail,
                        self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context.update({'id': self.kwargs['pk']})

        try:
            get_monitor = Monitor.objects.all().filter(
                agreement__id=self.kwargs['pk'])
        except Monitor.DoesNotExist:
            get_monitor = None
        context.update({'get_monitor': get_monitor})

        try:
            get_benchmark = Benchmarks.objects.all().filter(
                agreement__id=self.kwargs['pk'])
        except Benchmarks.DoesNotExist:
            get_benchmark = None
        context.update({'get_benchmarks': get_benchmark})

        try:
            get_budget = Budget.objects.all().filter(
                agreement__id=self.kwargs['pk'])
        except Budget.DoesNotExist:
            get_budget = None
        context.update({'get_budget': get_budget})

        try:
            get_documents = Documentation.objects.all().filter(
                project__id=self.kwargs['pk']).order_by('name')
        except Documentation.DoesNotExist:
            get_documents = None
        context.update({'get_documents': get_documents})

        try:
            get_quantitative_outputs = CollectedData.objects.all().filter(
                agreement__id=self.kwargs['pk'])

        except CollectedData.DoesNotExist:
            get_quantitative_outputs = None
        context.update({'get_quantitative_outputs': get_quantitative_outputs})

        return context


def delete_project_agreement(request, pk):
    project = ProjectAgreement.objects.get(pk=int(pk))
    project.delete()

    return redirect('/workflow/level2/list/0/none/')


class ProjectAgreementDelete(DeleteView):
    """
    Project Agreement Delete
    """
    model = ProjectAgreement
    success_url = '/workflow/dashboard/0/'

    @method_decorator(group_required('Country', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectAgreementDelete, self).dispatch(request, *args,
                                                            **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        return HttpResponseRedirect('/workflow/success')

    form_class = ProjectAgreementForm


class ProjectCompleteList(ListView):
    """
    Project Complete
    :param request:
    :param pk: program_id
    """
    model = ProjectComplete
    template_name = 'workflow/projectcomplete_list.html'

    def get(self, request, *args, **kwargs):
        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded", country__in=countries)

        if int(self.kwargs['pk']) == 0:
            get_dashboard = ProjectComplete.objects.all().filter(
                program__country__in=countries)
            return render(request, self.template_name,
                          {'get_dashboard': get_dashboard,
                           'get_programs': get_programs})
        else:
            get_dashboard = ProjectComplete.objects.all().filter(
                program__id=self.kwargs['pk'])
            get_program = Program.objects.get(id=self.kwargs['pk'])

            return render(request, self.template_name,
                          {'get_program': get_program,
                           'get_dashboard': get_dashboard,
                           'get_programs': get_programs})


class ProjectCompleteCreate(CreateView):
    """
    Project Complete Form
    """
    model = ProjectComplete
    template_name = 'workflow/projectcomplete_form.html'
    guidance = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Complete")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectCompleteCreate, self).dispatch(request, *args,
                                                           **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProjectCompleteCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    # get shared data from project agreement and pre-populate form with it
    def get_initial(self):
        get_project_agreement = ProjectAgreement.objects.get(
            id=self.kwargs['pk'])
        initial = {
            'approved_by': self.request.user,
            'approval_submitted_by': self.request.user,
            'program': get_project_agreement.program,
            'office': get_project_agreement.office,
            'sector': get_project_agreement.sector,
            'project_agreement': get_project_agreement.id,
            'project_name': get_project_agreement.project_name,
            'activity_code': get_project_agreement.activity_code,
            'expected_start_date': get_project_agreement.expected_start_date,
            'expected_end_date': get_project_agreement.expected_end_date,
            'expected_duration': get_project_agreement.expected_duration,
            'estimated_budget': get_project_agreement.total_estimated_budget,
            'short': get_project_agreement.short,
        }

        try:
            get_sites = SiteProfile.objects.filter(
                projectagreement__id=get_project_agreement.id).values_list(
                'id', flat=True)
            site = {'site': [o for o in get_sites]}
            initial['site'] = get_sites

        except SiteProfile.DoesNotExist:
            get_sites = None

        try:
            get_stakeholder = Stakeholder.objects.filter(
                projectagreement__id=get_project_agreement.id).values_list(
                'id', flat=True)
            stakeholder = {'stakeholder': [o for o in get_stakeholder], }
            initial['stakeholder'] = stakeholder
        except Stakeholder.DoesNotExist:
            get_stakeholder = None

        return initial

    def get_context_data(self, **kwargs):
        context = super(ProjectCompleteCreate, self).get_context_data(**kwargs)

        pk = self.kwargs['pk']
        context.update({'pk': pk})

        return context

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()
        context = self.get_context_data()
        self.object = form.save()

        latest = ProjectComplete.objects.latest('id')
        get_complete = ProjectComplete.objects.get(id=latest.id)
        get_agreement = ProjectAgreement.objects.get(
            id=self.request.POST['project_agreement'])

        # update the quantitative data fields to include the newly
        # created complete
        CollectedData.objects.filter(
            agreement__id=get_complete.project_agreement_id).update(
            complete=get_complete)

        # update the other budget items
        Budget.objects.filter(
            agreement__id=get_complete.project_agreement_id).update(
            complete=get_complete)

        # update the benchmarks
        Benchmarks.objects.filter(
            agreement__id=get_complete.project_agreement_id).update(
            complete=get_complete)

        # update main compelte fields
        ProjectComplete.objects.filter(id=get_complete.id).update(
            account_code=get_agreement.account_code,
            lin_code=get_agreement.lin_code)

        messages.success(self.request, 'Success, Tracking Form Created!')
        redirect_url = '/workflow/projectcomplete_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = ProjectCompleteCreateForm


class ProjectCompleteUpdate(UpdateView):
    """
    Project Tracking Form
    """
    model = ProjectComplete
    template_name = 'workflow/projectcomplete_form.html'
    guidance = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Complete")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectCompleteUpdate, self).dispatch(request, *args,
                                                           **kwargs)

    def get_form(self, form_class=None):
        check_form_type = ProjectComplete.objects.get(id=self.kwargs['pk'])

        if check_form_type.project_agreement.short:
            form_class = ProjectCompleteSimpleForm
        else:
            form_class = ProjectCompleteForm

        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(ProjectCompleteUpdate, self).get_context_data(**kwargs)
        get_complete = ProjectComplete.objects.get(id=self.kwargs['pk'])
        # id = get_complete.project_agreement_id

        context.update({'id': get_complete.pk})
        context.update({'p_name': get_complete.project_name})
        context.update({'p_complete_program': get_complete.program})
        pk = self.kwargs['pk']
        context.update({'pk': pk})
        context.update({'project_id': get_complete.project_agreement_id})

        # get budget data
        try:
            get_budget = Budget.objects.all().filter(
                Q(agreement__id=get_complete.project_agreement_id) | Q(
                    complete__id=get_complete.pk))
        except Budget.DoesNotExist:
            get_budget = None
        context.update({'get_budget': get_budget})

        # get Quantitative data
        try:
            get_quantitative = CollectedData.objects.all().filter(
                Q(agreement__id=get_complete.project_agreement_id) |
                Q(complete__id=get_complete.pk)).order_by('indicator')
        except CollectedData.DoesNotExist:
            get_quantitative = None
        context.update({'get_quantitative': get_quantitative})

        # get benchmark or project components
        try:
            get_benchmark = Benchmarks.objects.all().filter(
                Q(agreement__id=get_complete.project_agreement_id) |
                Q(complete__id=get_complete.pk)).order_by('description')
        except Benchmarks.DoesNotExist:
            get_benchmark = None
        context.update({'get_benchmark': get_benchmark})

        # get documents from the original agreement (documents are
        # not seperate in complete)
        try:
            get_documents = Documentation.objects.all().filter(
                project__id=get_complete.project_agreement_id).order_by('name')
        except Documentation.DoesNotExist:
            get_documents = None
        context.update({'get_documents': get_documents})

        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProjectCompleteUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    # get shared data from project agreement and pre-populate form with it
    def get_initial(self):
        initial = {
            'approved_by': self.request.user,
            'approval_submitted_by': self.request.user,
        }

        # update budget with new agreement
        try:
            get_budget = Budget.objects.all().filter(
                complete_id=self.kwargs['pk'])
            # if there aren't any budget try importing from the agreement
            if not get_budget:
                get_complete = ProjectComplete.objects.get(
                    id=self.kwargs['pk'])
                Budget.objects.filter(
                    agreement=get_complete.project_agreement_id).update(
                    complete_id=self.kwargs['pk'])
        except Budget.DoesNotExist:
            get_budget = None

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()
        self.object = form.save()

        messages.success(self.request, 'Success, form updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = ProjectCompleteForm


class ProjectCompleteDetail(DetailView):
    model = ProjectComplete
    context_object_name = 'complete'

    def get_object(self, queryset=ProjectComplete.objects.all()):
        try:
            return queryset.get(project_agreement__id=self.kwargs['pk'])
        except ProjectComplete.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):

        context = super(ProjectCompleteDetail, self).get_context_data(**kwargs)
        context['now'] = timezone.now()

        context.update({'id': self.kwargs['pk']})

        try:
            q_list = [Q(agreement__id=self.kwargs['pk'])]
            if self.get_object():
                q_list.append(Q(complete__id=self.get_object().pk))
            get_benchmark = Benchmarks.objects.filter(
                reduce(operator.or_, q_list))
        except Benchmarks.DoesNotExist:
            get_benchmark = None

        q_list = [Q(agreement__id=self.kwargs['pk'])]
        if self.get_object():
            q_list.append(Q(complete__id=self.get_object().pk))
        budget_contribs = Budget.objects.filter(reduce(operator.or_, q_list))

        context['budget_contribs'] = budget_contribs
        context['get_benchmarks'] = get_benchmark

        return context


class ProjectCompleteDelete(DeleteView):
    """
    Project Complete Delete
    """
    model = ProjectComplete
    success_url = '/workflow/projectcomplete_list/0/'

    @method_decorator(group_required('Country', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectCompleteDelete, self).dispatch(request, *args,
                                                           **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        return HttpResponseRedirect('/workflow/success')

    form_class = ProjectCompleteForm


class ProjectCompleteImport(ListView):

    def get_context_data(self, **kwargs):
        context = super(ProjectCompleteImport, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    template_name = 'workflow/projectcomplete_import.html'


class DocumentationList(ListView):
    """
    Documentation
    """
    model = Documentation
    template_name = 'workflow/documentation_list.html'

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['project']
        countries = get_country(request.user)
        user = ActivityUser.objects.filter(user=request.user).first()
        get_programs = Program.objects.all().filter(organization=user.organization)

        get_documentation = Documentation.objects.filter(program__organization=user.organization).select_related(
            'program')

        return render(request, self.template_name,
                      {'get_programs': get_programs,
                       'get_documentation': get_documentation,
                       'project_agreement_id': project_agreement_id,
                       'active': ['components', 'documents']})


class DocumentationAgreementList(AjaxableResponseMixin, CreateView):
    """
       Documentation Modal List
    """
    model = Documentation
    template_name = 'workflow/documentation_popup_list.html'

    def get(self, request, *args, **kwargs):
        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded", country__in=countries)

        get_documentation = Documentation.objects.all().prefetch_related(
            'program', 'project')

        return render(request, self.template_name,
                      {'get_programs': get_programs,
                       'get_documentation': get_documentation})


class DocumentationAgreementCreate(AjaxableResponseMixin, CreateView):
    """
    Documentation Form
    """
    model = Documentation
    template_name = 'workflow/documentation_popup_form.html'
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Documentation")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DocumentationAgreementCreate, self).dispatch(request,
                                                                  *args,
                                                                  **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DocumentationAgreementCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DocumentationAgreementCreate,
                        self).get_context_data(**kwargs)
        get_project = ProjectAgreement.objects.get(id=self.kwargs['id'])
        context.update({'program': get_project.program})
        context.update({'project': get_project})
        context.update({'id': self.kwargs['id']})
        return context

    def get_initial(self):
        get_project = ProjectAgreement.objects.get(id=self.kwargs['id'])
        initial = {
            'project': self.kwargs['id'],
            'program': get_project.program,
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Documentation Created!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DocumentationForm


class DocumentationAgreementUpdate(AjaxableResponseMixin, UpdateView):
    """
    Documentation Form
    """
    model = Documentation
    template_name = 'workflow/documentation_popup_form.html'
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Documentation")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DocumentationAgreementUpdate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DocumentationAgreementUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DocumentationAgreementUpdate,
                        self).get_context_data(**kwargs)
        get_project = ProjectAgreement.objects.get(id=self.kwargs['id'])
        context.update({'project': get_project})
        context.update({'id': self.kwargs['id']})
        context.update({'pk': self.kwargs['pk']})
        return context

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Documentation Updated!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DocumentationForm


class DocumentationAgreementDelete(AjaxableResponseMixin, DeleteView):
    """
    Documentation Delete popup window
    """
    model = Documentation
    template_name = 'workflow/documentation_agreement_confirm_delete.html'
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super(DocumentationAgreementDelete,
                        self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Documentation Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DocumentationForm


class DocumentationCreate(CreateView):
    """
    Documentation Form
    """
    model = Documentation
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Documentation")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DocumentationCreate, self).dispatch(request, *args,
                                                         **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DocumentationCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Documentation Created!')
        latest = Documentation.objects.latest('id')
        redirect_url = '/workflow/documentation_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = DocumentationForm


class DocumentationUpdate(UpdateView):
    """
    Documentation Form
    """
    model = Documentation
    queryset = Documentation.objects.select_related()
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Documentation")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DocumentationUpdate, self).dispatch(request, *args,
                                                         **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentationUpdate, self).get_context_data(**kwargs)
        documentation = Documentation.objects.get(pk=int(self.kwargs['pk']))
        context.update({'active': ['components', 'documents']})
        context.update({'documentation_name': documentation.name})

        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DocumentationUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()
        messages.success(self.request, 'Success, Documentation Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = DocumentationForm


class DocumentationDelete(DeleteView):
    """
    Documentation Form
    """
    model = Documentation
    success_url = '/workflow/documentation_list/0/0/'

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Documentation Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DocumentationForm


class IndicatorDataBySite(ListView):
    template_name = 'workflow/site_indicatordata.html'
    context_object_name = 'collecteddata'

    def get_context_data(self, **kwargs):
        context = super(IndicatorDataBySite, self).get_context_data(**kwargs)
        context['site'] = SiteProfile.objects.get(
            pk=self.kwargs.get('site_id'))
        return context

    def get_queryset(self):
        q = CollectedData.objects.filter(site__id=self.kwargs.get(
            'site_id')).order_by('program', 'indicator')
        return q


class ProjectCompleteBySite(ListView):
    template_name = 'workflow/site_projectcomplete.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super(ProjectCompleteBySite, self).get_context_data(**kwargs)
        context['site'] = SiteProfile.objects.get(
            pk=self.kwargs.get('site_id'))
        return context

    def get_queryset(self):
        q = ProjectComplete.objects.filter(
            site__id=self.kwargs.get('site_id')).order_by('program')
        return q


class SiteProfileList(ListView):
    """
    SiteProfile list creates a map and list of sites by user country access
    and filters by either direct link from project or by program
    dropdown filter
    """
    model = SiteProfile
    template_name = 'workflow/site_profile_list.html'

    def dispatch(self, request, *args, **kwargs):
        if 'report' in request.GET:
            template_name = 'workflow/site_profile_report.html'
        else:
            template_name = 'workflow/site_profile_list.html'
        return super(SiteProfileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # set the template
        if self.kwargs['display'] == 'map':
            self.template_name = 'workflow/site_profile_map.html'
        else:
            self.template_name = 'workflow/site_profile_list.html'

        activity_id = int(self.kwargs['activity_id'])
        program_id = int(self.kwargs['program_id'])

        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            organization=request.user.activity_user.organization)

        get_projects = ProjectAgreement.objects.filter(
            program__organization=request.user.activity_user.organization)

        # this date, 3 months ago, a site is considered inactive
        inactive_site = pytz.UTC.localize(
            datetime.now()) - relativedelta(months=3)

        # Filter SiteProfile list and map by activity or program
        if activity_id != 0:
            get_site_profile = SiteProfile.objects.all().prefetch_related(
                'country', 'district',
                'province').filter(
                projectagreement__id=activity_id).distinct()
        elif program_id != 0:
            get_site_profile = SiteProfile.objects.all().prefetch_related(
                'country', 'district', 'province').filter(
                Q(projectagreement__program__id=program_id) | Q(
                    collecteddata__program__id=program_id)).distinct()
        else:
            get_site_profile = SiteProfile.objects.all().prefetch_related(
                'country', 'district', 'province').filter(
                organizations=request.user.activity_user.organization
            ).distinct()
        if request.method == "GET" and "search" in request.GET:
            """
             fields = ('name', 'office')
            """
            get_site_profile = SiteProfile.objects.all() \
                .filter(Q(country__in=countries),
                        Q(name__contains=request.GET["search"]) |
                        Q(office__name__contains=request.GET["search"]) |
                        Q(type__profile__contains=request.GET['search']) |
                        Q(province__name__contains=request.GET["search"]) |
                        Q(district__name__contains=request.GET["search"]) |
                        Q(village__contains=request.GET['search']) |
                        Q(projectagreement__project_name__contains=request.GET[
                            "search"]) |
                        Q(projectcomplete__project_name__contains=request.GET[
                            'search'])) \
                .select_related().distinct()
        # paginate site profile list

        default_list = 10  # default number of site profiles per page
        # user defined number of site profiles per page, 10, 20, 30
        user_list = request.GET.get('user_list')

        if user_list:
            default_list = int(user_list)
        return render(request, self.template_name,
                      {
                          'inactive_site': inactive_site,
                          'default_list': default_list,
                          'get_site_profile': get_site_profile,
                          'project_agreement_id': activity_id,
                          'country': countries,
                          'get_programs': get_programs,
                          'get_projects': get_projects,
                          'form': FilterForm(),
                          'helper': FilterForm.helper,
                          'active': ['components'],
                          'map_api_key': settings.GOOGLE_MAP_API_KEY
                      })


class SiteProfileReport(ListView):
    """
    SiteProfile Report filtered by project
    """
    model = SiteProfile
    template_name = 'workflow/site_profile_report.html'

    def get(self, request, *args, **kwargs):
        countries = get_country(request.user)
        project_agreement_id = self.kwargs['pk']

        if int(self.kwargs['pk']) == 0:
            get_site_profile = SiteProfile.objects.all().prefetch_related(
                'country', 'district', 'province').filter(
                country__in=countries).filter(status=1)
            get_site_profile_indicator = SiteProfile.objects.all() \
                .prefetch_related('country', 'district', 'province').filter(
                Q(collecteddata__program__country__in=countries)).filter(
                status=1)
        else:
            get_site_profile = SiteProfile.objects.all().prefetch_related(
                'country', 'district', 'province').filter(
                projectagreement__id=self.kwargs['pk']).filter(status=1)
            get_site_profile_indicator = None

        id = self.kwargs['pk']

        return render(request, self.template_name,
                      {'get_site_profile': get_site_profile,
                       'get_site_profile_indicator':
                           get_site_profile_indicator,
                       'project_agreement_id': project_agreement_id, 'id': id,
                       'country': countries})


class SiteProfileCreate(CreateView):
    """
    Using SiteProfile Form, create a new site profile
    """
    model = SiteProfile
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="SiteProfile")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(SiteProfileCreate, self).dispatch(request, *args,
                                                       **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(SiteProfileCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        countries = get_country(self.request.user)
        default_country = None
        if countries:
            default_country = countries[0]
        initial = {
            'approved_by': self.request.user,
            'filled_by': self.request.user,
            'country': default_country,
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        instance = form.save()
        instance.organizations.add(self.request.user.activity_user.organization)
        messages.success(self.request, 'Success, Site Profile Created!')
        latest = SiteProfile.objects.latest('id')
        redirect_url = '/workflow/siteprofile_list/0/0/list/'
        return HttpResponseRedirect(redirect_url)

    form_class = SiteProfileForm


class SiteProfileUpdate(UpdateView):
    """
    SiteProfile Form Update an existing site profile
    """
    model = SiteProfile
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="SiteProfile")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(SiteProfileUpdate, self).dispatch(request, *args,
                                                       **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(SiteProfileUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SiteProfileUpdate, self).get_context_data(**kwargs)
        site = SiteProfile.objects.get(pk=int(self.kwargs['pk']))
        get_projects = ProjectAgreement.objects.all().filter(
            site__id=self.kwargs['pk'])
        context.update({'get_projects': get_projects})
        context.update({'site_name': site.name})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, SiteProfile Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = SiteProfileForm


class SiteProfileDelete(DeleteView):
    """
    SiteProfile Form Delete an existing community
    """
    model = SiteProfile
    success_url = "/workflow/siteprofile_list/0/0/"

    @method_decorator(group_required('Country', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(SiteProfileDelete, self).dispatch(request, *args,
                                                       **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, SiteProfile Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = SiteProfileForm


class MonitorList(ListView):
    """
    Monitoring Data
    """
    model = Monitor
    template_name = 'workflow/monitor_list.html'

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['pk']

        if int(self.kwargs['pk']) == 0:
            get_monitor_data = Monitor.objects.all()
        else:
            get_monitor_data = Monitor.objects.all().filter(
                agreement__id=self.kwargs['pk'])

        if int(self.kwargs['pk']) == 0:
            get_benchmark_data = Benchmarks.objects.all()
        else:
            get_benchmark_data = Benchmarks.objects.all().filter(
                agreement__id=self.kwargs['pk'])

        return render(request, self.template_name,
                      {'get_monitor_data': get_monitor_data,
                       'get_benchmark_data': get_benchmark_data,
                       'project_agreement_id': project_agreement_id})


class MonitorCreate(AjaxableResponseMixin, CreateView):
    """
    Monitor Form
    """
    model = Monitor

    def dispatch(self, request, *args, **kwargs):
        return super(MonitorCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MonitorCreate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    def get_initial(self):
        initial = {
            'agreement': self.kwargs['id'],
        }

        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Monitor Created!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = MonitorForm


class MonitorUpdate(AjaxableResponseMixin, UpdateView):
    """
    Monitor Form
    """
    model = Monitor

    def get_context_data(self, **kwargs):
        context = super(MonitorUpdate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Monitor Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = MonitorForm


class MonitorDelete(AjaxableResponseMixin, DeleteView):
    """
    Monitor Form
    """
    model = Monitor
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(MonitorDelete, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Monitor Deleted!')
        return self.render_to_response(self.get_context_data(form=form))


class BenchmarkCreate(AjaxableResponseMixin, CreateView):
    """
    Benchmark Form
    """
    model = Benchmarks

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BenchmarkCreate, self).get_form_kwargs()
        try:
            get_complete = ProjectComplete.objects.get(
                project_agreement__id=self.kwargs['id'])
            kwargs['complete'] = get_complete.id
        except ProjectComplete.DoesNotExist:
            kwargs['complete'] = None

        kwargs['request'] = self.request
        kwargs['agreement'] = self.kwargs['id']
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        return super(BenchmarkCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BenchmarkCreate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        try:
            get_complete = ProjectComplete.objects.get(id=self.kwargs['id'])
            context.update({'p_name': get_complete.project_name})
        except ProjectComplete.DoesNotExist:
            # do nothing
            context = context
        return context

    def get_initial(self):

        if self.request.GET.get('is_it_project_complete_form', None):
            initial = {'complete': self.kwargs['id']}
        else:
            initial = {'agreement': self.kwargs['id']}

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Component Created!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BenchmarkForm


class BenchmarkUpdate(AjaxableResponseMixin, UpdateView):
    """
    Benchmark Form
    """
    model = Benchmarks

    def get_context_data(self, **kwargs):
        context = super(BenchmarkUpdate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BenchmarkUpdate, self).get_form_kwargs()
        get_benchmark = Benchmarks.objects.all().get(id=self.kwargs['pk'])

        kwargs['request'] = self.request
        kwargs['agreement'] = get_benchmark.agreement.id
        if get_benchmark.complete:
            kwargs['complete'] = get_benchmark.complete.id
        else:
            kwargs['complete'] = None

        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Component Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = BenchmarkForm


class BenchmarkDelete(AjaxableResponseMixin, DeleteView):
    """
    Benchmark Form
    """
    model = Benchmarks
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(BenchmarkDelete, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Component Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BenchmarkForm


class ContactList(ListView):
    """
    Get Contacts
    """
    model = Contact
    template_name = 'workflow/contact_list.html'

    def get(self, request, *args, **kwargs):
        user = ActivityUser.objects.filter(user=request.user).first()

        get_contacts = Contact.objects.filter(organization=user.organization)

        return render(request, self.template_name, {
            'get_contacts': get_contacts
        })


class ContactCreate(CreateView):
    """
    Contact Form
    """
    model = Contact
    stakeholder_id = None
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Contact")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ContactCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactCreate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        context.update({'stakeholder_id': self.kwargs['stakeholder_id']})
        return context

    def get_initial(self):
        country = get_country(self.request.user)[0]
        initial = {
            'agreement': self.kwargs['id'],
            'country': country,
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Contact Created!')
        latest = Contact.objects.latest('id')
        redirect_url = '/workflow/contact_update/' + \
                       self.kwargs['stakeholder_id'] + '/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = ContactForm


class ContactUpdate(UpdateView):
    """
    Contact Form
    """
    model = Contact
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Contact")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ContactUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactUpdate, self).get_context_data(**kwargs)
        contact = Contact.objects.get(pk=int(self.kwargs['pk']))
        context.update({'contact_name': contact.name})
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Contact Updated!')

        return redirect('/workflow/contact_list/0/')

    form_class = ContactForm


def delete_contact(request, pk):
    contact = Contact.objects.get(pk=int(pk))
    contact.delete()

    return redirect('/workflow/contact_list/0/')


class CountryDoesNotExist(Exception):
    """Raised when there is no country in database"""
    pass


class StakeholderList(ListView):
    """
    get_stakeholders
    """
    model = Stakeholder
    template_name = 'workflow/stakeholder_list.html'

    def get(self, request, *args, **kwargs):
        # Check for project filter
        # project_agreement_id = self.kwargs['pk']

        get_stakeholders = Stakeholder.objects.all().filter(
            organization=self.request.user.activity_user.organization)

        return render(request, self.template_name,
                      {'get_stakeholders': get_stakeholders,
                       'get_stakeholder_types': StakeholderType.objects.all(),
                       'get_sectors': Sector.objects.all(),
                       'active': ['components', 'stakeholders']})


class StakeholderCreate(CreateView):
    """
    Stakeholder Form
    """
    model = Stakeholder
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Stakeholder")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(StakeholderCreate, self).dispatch(request, *args,
                                                       **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(StakeholderCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(StakeholderCreate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    def get_initial(self):

        country = get_country(self.request.user).first()

        initial = {
            'agreement': self.kwargs['id'],
            'country': country,
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Stakeholder Created!')
        latest = Stakeholder.objects.latest('id')
        redirect_url = '/workflow/stakeholder_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = StakeholderForm


class StakeholderUpdate(UpdateView):
    """
    Stakeholder Form
    """
    model = Stakeholder
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Stakeholder")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(StakeholderUpdate, self).dispatch(request, *args,
                                                       **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(StakeholderUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(StakeholderUpdate, self).get_context_data(**kwargs)
        stakeholder = Stakeholder.objects.get(pk=int(self.kwargs['pk']))
        context.update({'id': self.kwargs['pk']})
        context.update({'stakeholder_name': stakeholder.name})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Stakeholder Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = StakeholderForm


class StakeholderDelete(DeleteView):
    """
    Benchmark Form
    """
    model = Stakeholder
    success_url = '/workflow/stakeholder_list/0/0/'

    def get_context_data(self, **kwargs):
        context = super(StakeholderDelete, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Stakeholder Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = StakeholderForm


class QuantitativeOutputsCreate(AjaxableResponseMixin, CreateView):
    """
    QuantitativeOutput Form
    """
    model = CollectedData
    template_name = 'workflow/quantitativeoutputs_form.html'

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(QuantitativeOutputsCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(QuantitativeOutputsCreate,
                        self).get_context_data(**kwargs)
        is_it_project_complete_form = self.request.GET.get(
            'is_it_project_complete_form', None) or \
            self.request.POST.get(
            'is_it_project_complete_form', None)
        if is_it_project_complete_form == 'true':
            get_program = Program.objects.get(complete__id=self.kwargs['id'])
        else:
            get_program = Program.objects.get(agreement__id=self.kwargs['id'])
        context.update({'id': self.kwargs['id']})
        context.update({'program': get_program})
        return context

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(QuantitativeOutputsCreate, self).dispatch(request, *args,
                                                               **kwargs)

    def get_initial(self):
        is_it_project_complete_form = self.request.GET.get(
            'is_it_project_complete_form', None) or \
            self.request.POST.get(
            'is_it_project_complete_form', None)

        if is_it_project_complete_form == 'true':
            get_program = Program.objects.get(complete__id=self.kwargs['id'])
            initial = {
                'complete': self.kwargs['id'],
                'program': get_program.id,
                'is_it_project_complete_form': 'true',
            }
        else:
            get_program = Program.objects.get(agreement__id=self.kwargs['id'])
            initial = {
                'agreement': self.kwargs['id'],
                'program': get_program.id,
                'is_it_project_complete_form': 'false',
            }
        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Quantitative Output Created!')
        form = ""
        return self.render_to_response(self.get_context_data(form=form))

    form_class = QuantitativeOutputsForm


class QuantitativeOutputsUpdate(AjaxableResponseMixin, UpdateView):
    """
    QuantitativeOutput Form
    """
    model = CollectedData
    template_name = 'workflow/quantitativeoutputs_form.html'

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(QuantitativeOutputsUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(QuantitativeOutputsUpdate, self).dispatch(request, *args,
                                                               **kwargs)

    def get_initial(self):
        """
        get the program to filter the list and indicators by.. the FK to
        colelcteddata is i_program we should change that name at somepoint
        as it is very confusing
        """
        get_program = Program.objects.get(i_program__pk=self.kwargs['pk'])
        # indicator = Indicator.objects.get(id)
        is_it_project_complete_form = self.request.GET.get(
            'is_it_project_complete_form', None) or \
            self.request.POST.get(
            'is_it_project_complete_form', None)

        initial = {
            'program': get_program.id,
            'is_it_project_complete_form':
                'true' if is_it_project_complete_form else 'false',
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(QuantitativeOutputsUpdate,
                        self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Quantitative Output Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = QuantitativeOutputsForm


class QuantitativeOutputsDelete(AjaxableResponseMixin, DeleteView):
    """
    QuantitativeOutput Delete
    """
    model = CollectedData

    # success_url = '/'

    def get_success_url(self):
        return self.request.GET.get('redirect_uri', '/')

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(QuantitativeOutputsDelete, self).dispatch(request, *args,
                                                               **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Quantitative Output Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = QuantitativeOutputsForm


class BudgetList(ListView):
    """
    Budget List
    """
    model = Budget
    template_name = 'workflow/budget_list.html'

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['pk']

        if int(self.kwargs['pk']) == 0:
            get_budget = Budget.objects.all()
        else:
            get_budget = Budget.objects.all().filter(
                project_agreement_id=self.kwargs['pk'])

        return render(request, self.template_name,
                      {'get_budget': get_budget,
                       'project_agreement_id': project_agreement_id})


class BudgetCreate(AjaxableResponseMixin, CreateView):
    """
    Budget Form
    """
    model = Budget
    template_name = 'workflow/budget_form.html'

    def get_context_data(self, **kwargs):
        context = super(BudgetCreate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(BudgetCreate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        if self.request.GET.get('is_it_project_complete_form', None):
            initial = {'complete': self.kwargs['id']}
        else:
            initial = {'agreement': self.kwargs['id']}
        return initial

    def get_form_kwargs(self):
        kwargs = super(BudgetCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        obj = form.save()
        if self.request.is_ajax():
            data = serializers.serialize('json', [obj])
            return HttpResponse(data)

        messages.success(self.request, 'Success, Budget Created!')
        form = ""
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BudgetForm


class BudgetUpdate(AjaxableResponseMixin, UpdateView):
    """
    Budget Form
    """
    model = Budget

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(BudgetUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BudgetUpdate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BudgetUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        obj = form.save()
        if self.request.is_ajax():
            data = serializers.serialize('json', [obj])
            return HttpResponse(data)

        messages.success(self.request, 'Success, Budget Output Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = BudgetForm


class BudgetDelete(AjaxableResponseMixin, DeleteView):
    """
    Budget Delete
    """
    model = Budget
    success_url = '/'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(BudgetDelete, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BudgetDelete, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Budget Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BudgetForm


class ChecklistItemList(ListView):
    """
    Checklist List
    """
    model = ChecklistItem
    template_name = 'workflow/checklist_list.html'

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['pk']

        if int(self.kwargs['pk']) == 0:
            get_checklist = ChecklistItem.objects.all()
        else:
            get_checklist = ChecklistItem.objects.all().filter(
                checklist__agreement_id=self.kwargs['pk'])

        return render(request, self.template_name,
                      {'get_checklist': get_checklist,
                       'project_agreement_id': self.kwargs['pk']})


class ChecklistItemCreate(CreateView):
    """
    Checklist Form
    """
    model = ChecklistItem
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="ChecklistItem")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ChecklistItemCreate, self).dispatch(request, *args,
                                                         **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChecklistItemCreate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ChecklistItemCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ChecklistItemCreate, self).dispatch(request, *args,
                                                         **kwargs)

    def get_initial(self):
        checklist = Checklist.objects.get(agreement=self.kwargs['id'])
        initial = {
            'checklist': checklist,
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Checklist Item Created!')
        latest = ChecklistItem.objects.latest('id')
        redirect_url = '/workflow/checklistitem_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = ChecklistItemForm


class ChecklistItemUpdate(UpdateView):
    """
    Checklist Form
    """
    model = ChecklistItem
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="ChecklistItem")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ChecklistItemUpdate, self).dispatch(request, *args,
                                                         **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChecklistItemUpdate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ChecklistItemUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Checklist Item Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = ChecklistItemForm


def checklist_update_link(AjaxableResponseMixin, pk, type, value):
    """
    Checklist Update from Link
    """
    value = int(value)

    if type == "in_file":
        update = ChecklistItem.objects.filter(id=pk).update(in_file=value)
    elif type == "not_applicable":
        update = ChecklistItem.objects.filter(id=pk).update(
            not_applicable=value)

    return HttpResponse(value)


class ChecklistItemDelete(DeleteView):
    """
    Checklist Delete
    """
    model = ChecklistItem
    success_url = '/'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ChecklistItemDelete, self).dispatch(request, *args,
                                                         **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChecklistItemDelete, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Checklist Item Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = ChecklistItemForm


class Report(View, AjaxableResponseMixin):
    """
    project agreement list report
    """

    def get(self, request, *args, **kwargs):

        countries = get_country(request.user)
        organization = request.user.activity_user.organization

        if int(self.kwargs['pk']) != 0:
            get_agreements = ProjectAgreement.objects.all().filter(
                program__id=self.kwargs['pk'])

        elif self.kwargs['status'] != 'none':
            get_agreements = ProjectAgreement.objects.all().filter(
                approval=self.kwargs['status'])
        else:
            get_agreements = ProjectAgreement.objects.select_related().filter(
                program__organization=organization)

        get_programs = Program.objects.all().filter(
            funding_status="Funded", organization=organization)

        filtered = ProjectAgreementFilter(request.GET, queryset=get_agreements)
        table = ProjectAgreementTable(filtered.queryset)
        table.paginate(page=request.GET.get('page', 1), per_page=20)

        if request.method == "GET" and "search" in request.GET:
            get_agreements = ProjectAgreement.objects.filter(
                Q(project_name__contains=request.GET["search"]) |
                Q(activity_code__contains=request.GET["search"]))

        if request.GET.get('export'):
            dataset = ProjectAgreementResource().export(get_agreements)
            response = HttpResponse(
                dataset.csv, content_type='application/ms-excel')
            response[
                'Content-Disposition'] = \
                'attachment; filename=activity_report.csv'
            return response

        # send the keys and vars
        return render(request, "workflow/report.html",
                      {'country': countries, 'form': FilterForm(),
                       'filter': filtered, 'helper': FilterForm.helper,
                       'APPROVALS': APPROVALS, 'get_programs': get_programs})


class ReportData(View, AjaxableResponseMixin):
    """
    Render Agreements json object response to the report ajax call
    """

    def get(self, request, *args, **kwargs):
        organization = request.user.activity_user.organization
        filters = {}
        if int(self.kwargs['pk']) != 0:
            filters['program__id'] = self.kwargs['pk']
        elif self.kwargs['status'] != 'none':
            filters['approval'] = self.kwargs['status']
        else:
            filters['program__organization'] = organization

        get_agreements = ProjectAgreement.objects.prefetch_related('sectors') \
            .select_related('program', 'project_type', 'office',
                            'estimated_by').filter(**filters) \
            .values('id', 'program__id', 'approval', 'program__name',
                    'project_name', 'site', 'activity_code',
                    'office__name', 'project_name', 'sector__sector',
                    'project_activity', 'project_type__name',
                    'account_code', 'lin_code', 'estimated_by__name',
                    'total_estimated_budget',
                    'mc_estimated_budget', 'total_estimated_budget')

        get_agreements = json.dumps(list(get_agreements),
                                    cls=DjangoJSONEncoder)

        final_dict = {'get_agreements': get_agreements}

        return JsonResponse(final_dict, safe=False)


def country_json(request, country):
    """
    For populating the province dropdown based  country dropdown value
    """
    selected_country = Country.objects.get(id=country)
    province = Province.objects.all().filter(country=selected_country)
    provinces_json = serializers.serialize("json", province)
    return HttpResponse(provinces_json, content_type="application/json")


def province_json(request, province):
    """
    For populating the office district based  country province value
    """
    selected_province = Province.objects.get(id=province)
    district = District.objects.all().filter(province=selected_province)
    districts_json = serializers.serialize("json", district)
    return HttpResponse(districts_json, content_type="application/json")


def district_json(request, district):
    """
    For populating the office dropdown based  country dropdown value
    """
    selected_district = District.objects.get(id=district)
    adminthree = AdminLevelThree.objects.all().filter(
        district=selected_district)
    adminthree_json = serializers.serialize("json", adminthree)
    return HttpResponse(adminthree_json, content_type="application/json")


def import_service(service_id=1, deserialize=True):
    """
    Import a indicators from a web service (the dig only for now)
    """
    service = ExternalService.objects.all().filter(id=service_id)

    response = requests.get(service.feed_url)
    get_json = json.loads(response.content)

    if deserialize:
        data = json.load(get_json)  # deserialises it
    else:
        # send json data back not deserialized data
        data = get_json
    # debug the json data string uncomment dump and print
    data2 = json.dumps(data)  # json formatted string

    return data


def service_json(request, service):
    """
    For populating service indicators in dropdown
    """
    service_indicators = import_service(service, deserialize=False)
    return HttpResponse(service_indicators, content_type="application/json")


def export_stakeholders_list(request, **kwargs):
    program_id = int(kwargs['program_id'])
    countries = get_country(request.user)

    if program_id != 0:
        get_stakeholders = Stakeholder.objects.prefetch_related(
            'sector').filter(
            projectagreement__program__id=program_id).distinct()
    else:
        get_stakeholders = Stakeholder.objects.prefetch_related(
            'sector').filter(country__in=countries)

    dataset = StakeholderResource().export(get_stakeholders)
    response = HttpResponse(dataset.csv, content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=stakeholders.csv'

    return response


def export_sites_list(request, **kwargs):
    # program_id = int(kwargs['program_id'])
    countries = get_country(request.user)

    # if program_id != 0:
    #    get_sites = Sites.objects.prefetch_related('sector').filter(
    #    projectagreement__program__id=program_id).distinct()
    # else:
    get_sites = SiteProfile.objects.prefetch_related(
        'sector').filter(country__in=countries)

    dataset = SiteProfileResource().export(get_sites)
    response = HttpResponse(dataset.csv, content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=sites.csv'

    return response


def save_bookmark(request):
    """
    Create Bookmark from Link
    """
    url = request.POST['url']
    username = request.user
    activity_user = ActivityUser.objects.get(user=username)

    ActivityBookmarks.objects.create(bookmark_url=url, name=url,
                                     user=activity_user)

    return HttpResponse(url)


# Ajax views for single page filtering
class StakeholderObjects(View, AjaxableResponseMixin):
    """
    Render Agreements json object response to the report ajax call
    """

    def get(self, request, *args, **kwargs):

        # Check for project filter
        project_agreement_id = self.kwargs['pk']
        # Check for program filter

        if self.kwargs['program_id']:
            program_id = int(self.kwargs['program_id'])
        else:
            program_id = 0

        countries = get_country(request.user)

        countries = get_country(request.user)

        if program_id != 0:
            get_stakeholders = Stakeholder.objects.all().filter(
                projectagreement__program__id=program_id).distinct(
            ).values('id', 'create_date', 'type__name', 'name',
                     'sectors__sector')

        elif int(self.kwargs['pk']) != 0:
            get_stakeholders = Stakeholder.objects.all().filter(
                projectagreement=self.kwargs['pk']).distinct(
            ).values('id', 'create_date', 'type__name', 'name',
                     'sectors__sector')

        else:
            get_stakeholders = Stakeholder.objects.all().filter(
                country__in=countries).values(
                'id', 'create_date', 'type__name', 'name', 'sectors__sector')

        get_stakeholders = json.dumps(
            list(get_stakeholders), cls=DjangoJSONEncoder)

        final_dict = {'get_stakeholders': get_stakeholders}

        return JsonResponse(final_dict, safe=False)


class SiteProfileObjects(View, AjaxableResponseMixin):
    """
    Render Agreements json object response to the report ajax call
    """

    def get(self, request, *args, **kwargs):

        # Check for project filter
        project_agreement_id = self.kwargs['pk']
        # Check for program filter

        if self.kwargs['program_id']:
            program_id = int(self.kwargs['program_id'])
        else:
            program_id = 0

        countries = get_country(request.user)

        countries = get_country(request.user)

        if program_id != 0:
            get_sites = SiteProfile.objects.all().filter(
                projectagreement__program__id=program_id).distinct().values(
                'id')

        elif int(self.kwargs['pk']) != 0:
            get_sites = SiteProfile.objects.all().filter(
                projectagreement=self.kwargs['pk']).distinct().values('id')

        else:
            get_sites = SiteProfile.objects.all().filter(
                country__in=countries).values('id')

        get_sites = json.dumps(list(get_sites), cls=DjangoJSONEncoder)

        final_dict = {'get_sites': get_sites}

        return JsonResponse(final_dict, safe=False)


class DocumentationListObjects(View, AjaxableResponseMixin):

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['project']
        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded", country__in=countries)

        if int(self.kwargs['program']) != 0 & int(self.kwargs['project']) == 0:
            get_documentation = Documentation.objects.all().prefetch_related(
                'program', 'project').filter(
                program__id=self.kwargs['program']).values(
                'id', 'name',
                'project__project_name',
                'create_date')
        elif int(self.kwargs['project']) != 0:
            get_documentation = Documentation.objects.all().prefetch_related(
                'program', 'project').filter(
                project__id=self.kwargs['project']).values(
                'id', 'name',
                'project__project_name',
                'create_date')
        else:
            countries = get_country(request.user)
            get_documentation = Documentation.objects.all().prefetch_related(
                'program', 'project', 'project__office') \
                .filter(program__country__in=countries).values(
                'id', 'name',
                'project__project_name',
                'create_date')

        get_documentation = json.dumps(
            list(get_documentation), cls=DjangoJSONEncoder)
        final_dict = {'get_documentation': get_documentation}

        return JsonResponse(final_dict, safe=False)


def add_level2(request):
    data = request.POST
    program = Program.objects.get(id=int(data.get('program')))

    level2 = ProjectAgreement(project_name=data.get(
        'project_name'), program=program)

    if level2.save():
        return HttpResponse({'success': True})

    return HttpResponse({'success': False})


def add_documentation(request):
    data = request.POST
    program = Program.objects.get(id=int(data.get('program')))

    documentation = Documentation(name=data.get(
        'name'), url=data.get('url'), program=program)

    if documentation.save():
        return HttpResponse({'success': True})

    return HttpResponse({'success': False})


def add_contact(request):
    data = request.POST

    user = ActivityUser.objects.filter(user=request.user).first()

    contact = Contact(name=data.get('name'), city=data.get('city'), address=data.get(
        'address'), phone=data.get('phone_number'), organization=user.organization)

    if contact.save():
        return HttpResponse({'success': True})

    return HttpResponse({'success': False})


def add_stakeholder(request):
    data = request.POST

    user = ActivityUser.objects.filter(user=request.user).first()

    stakeholder_type_id = int(data.get('stakeholder_type', None), 10)
    sector_ids = list(map(int, data.getlist('sectors[]', [])))

    stakeholder = Stakeholder(name=data.get(
        'stakeholder_name'), type_id=stakeholder_type_id, organization=user.organization, stakeholder_register=False)
    stakeholder.save()

    if stakeholder.id:
        sectors = Sector.objects.filter(id__in=sector_ids)
        stakeholder.sectors.set(sectors)
        return HttpResponse({'success': True})

    return HttpResponse({'success': False})
