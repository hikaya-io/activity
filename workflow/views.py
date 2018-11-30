import operator
import unicodedata

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Program, Country, Province, AdminLevelThree, District, ProjectAgreement, ProjectComplete, SiteProfile, \
    Documentation, Monitor, Benchmarks, Budget, ApprovalAuthority, Checklist, ChecklistItem, Contact, Stakeholder, FormGuidance, \
    TolaBookmarks, TolaUser
from formlibrary.models import TrainingAttendance, Distribution
from indicators.models import CollectedData, ExternalService
from django.utils import timezone


from .forms import ProjectAgreementForm, ProjectAgreementSimpleForm, ProjectAgreementCreateForm, ProjectCompleteForm, ProjectCompleteSimpleForm, ProjectCompleteCreateForm, DocumentationForm, \
    SiteProfileForm, MonitorForm, BenchmarkForm, BudgetForm, FilterForm, \
    QuantitativeOutputsForm, ChecklistItemForm, StakeholderForm, ContactForm

import pytz

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q
from tables import ProjectAgreementTable
from filters import ProjectAgreementFilter
import json
import requests
import logging

from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.detail import View

from django.contrib.sites.shortcuts import get_current_site

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.utils.decorators import method_decorator
from tola.util import getCountry, emailGroup, group_excluded, group_required
from mixins import AjaxableResponseMixin
from export import ProjectAgreementResource, StakeholderResource, SiteProfileResource

APPROVALS = (
    ('in_progress',('in progress')),
    ('awaiting_approval', 'awaiting approval'),
    ('approved', 'approved'),
    ('rejected', 'rejected'),
)

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.serializers.json import DjangoJSONEncoder


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


class ProjectDash(ListView):

    template_name = 'workflow/projectdashboard_list.html'

    def get(self, request, *args, **kwargs):

        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)
        project_id = int(self.kwargs['pk'])

        if project_id == 0:
            getAgreement = None
            getComplete = None
            getChecklist = None
            getDocumentCount = 0
            getCommunityCount = 0
            getTrainingCount = 0
            getDistributionCount = 0
            getChecklistCount = 0
        else:
            getAgreement = ProjectAgreement.objects.get(id=project_id)
            try:
                getComplete = ProjectComplete.objects.get(project_agreement__id=self.kwargs['pk'])
            except ProjectComplete.DoesNotExist:
                getComplete = None
            getDocumentCount = Documentation.objects.all().filter(project_id=self.kwargs['pk']).count()
            getCommunityCount = SiteProfile.objects.all().filter(projectagreement__id=self.kwargs['pk']).count()
            getTrainingCount = TrainingAttendance.objects.all().filter(project_agreement_id=self.kwargs['pk']).count()
            getDistributionCount = Distribution.objects.all().filter(initiation_id=self.kwargs['pk']).count()
            getChecklistCount = ChecklistItem.objects.all().filter(checklist__agreement_id=self.kwargs['pk']).count()
            getChecklist = ChecklistItem.objects.all().filter(checklist__agreement_id=self.kwargs['pk'])

        if int(self.kwargs['pk']) == 0:
            getProgram =Program.objects.all().filter(funding_status="Funded", country__in=countries).distinct()
        else:
            getProgram =Program.objects.get(agreement__id=self.kwargs['pk'])

        return render(request, self.template_name, {'getProgram': getProgram, 'getAgreement': getAgreement,'getComplete': getComplete,
                                                    'getPrograms':getPrograms, 'getDocumentCount':getDocumentCount,'getChecklistCount': getChecklistCount,
                                                    'getCommunityCount':getCommunityCount, 'getTrainingCount':getTrainingCount, 'project_id': project_id,
                                                    'getChecklist': getChecklist, 'getDistributionCount': getDistributionCount})


class ProgramDash(ListView):
    """
    Dashboard links for and status for each program with number of projects
    :param request:
    :param pk: program_id
    :param status: approval status of project
    :return:
    """
    template_name = 'workflow/programdashboard_list.html'

    def get(self, request, *args, **kwargs):

        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries).distinct()
        filtered_program = None
        if int(self.kwargs['pk']) == 0:
            getDashboard = Program.objects.all().prefetch_related('agreement','agreement__projectcomplete','agreement__office').filter(funding_status="Funded", country__in=countries).order_by('name').annotate(has_agreement=Count('agreement'),has_complete=Count('complete'))
        else:
            getDashboard = Program.objects.all().prefetch_related('agreement','agreement__projectcomplete','agreement__office').filter(id=self.kwargs['pk'], funding_status="Funded", country__in=countries).order_by('name')
            filtered_program = Program.objects.only('name').get(pk=self.kwargs['pk']).name

        if self.kwargs.get('status', None):

            status = self.kwargs['status']
            if status == "in_progress":
                getDashboard.filter(Q(agreement__approval=self.kwargs['status']) | Q(agreement__approval=None))

            elif status == "new":
                getDashboard.filter(Q(Q(agreement__approval=None) | Q(agreement__approval="")))

            else:
                getDashboard.filter(agreement__approval=self.kwargs['status'])
        else:
            status = None

        return render(request, self.template_name, {'getDashboard': getDashboard, 'getPrograms': getPrograms, 'APPROVALS': APPROVALS, 'program_id':  self.kwargs['pk'], 'status': status, 'filtered_program': filtered_program})


class ProjectAgreementList(ListView):
    """
    Project Agreement
    :param request:
    """
    model = ProjectAgreement
    template_name = 'workflow/projectagreement_list.html'

    def get(self, request, *args, **kwargs):
        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries).distinct()

        if int(self.kwargs['pk']) != 0:
            getDashboard = ProjectAgreement.objects.all().filter(program__id=self.kwargs['pk'])
            getProgram =Program.objects.get(id=self.kwargs['pk'])
            return render(request, self.template_name, {'form': FilterForm(),'getProgram': getProgram, 'getDashboard':getDashboard,'getPrograms':getPrograms,'APPROVALS': APPROVALS})

        elif self.kwargs['status'] != 'none':
            getDashboard = ProjectAgreement.objects.all().filter(approval=self.kwargs['status'])
            return render(request, self.template_name, {'form': FilterForm(), 'getDashboard':getDashboard,'getPrograms':getPrograms,'APPROVALS': APPROVALS})

        else:
            getDashboard = ProjectAgreement.objects.all().filter(program__country__in=countries)

            return render(request, self.template_name, {'form': FilterForm(),'getDashboard':getDashboard,'getPrograms':getPrograms,'APPROVALS': APPROVALS})


class ProjectAgreementImport(ListView):
    """
    Import a project agreement from TolaData or other third party service
    """

    template_name = 'workflow/projectagreement_import.html'

    def get(self, request, *args, **kwargs):
        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)
        getServices = ExternalService.objects.all()
        getCountries = Country.objects.all().filter(country__in=countries)

        return render(request, self.template_name, {'getPrograms': getPrograms, 'getServices': getServices , 'getCountries': getCountries})


class ProjectAgreementCreate(CreateView):
    """
    Project Agreement Form
    :param request:
    :param id:
    This is only used in case of an error incomplete form submission from the simple form
    in the project dashboard
    """

    model = ProjectAgreement
    template_name = 'workflow/projectagreement_form.html'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Agreement")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectAgreementCreate, self).dispatch(request, *args, **kwargs)

     # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProjectAgreementCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    #get shared data from project agreement and pre-populate form with it
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
        context = super(ProjectAgreementCreate, self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        #save formset from context
        context = self.get_context_data()

        latest = ProjectAgreement.objects.latest('id')
        getAgreement = ProjectAgreement.objects.get(id=latest.id)

        #create a new dashbaord entry for the project
        getProgram = Program.objects.get(id=latest.program_id)

        create_checklist = Checklist(agreement=getAgreement)
        create_checklist.save()

        get_checklist = Checklist.objects.get(id=create_checklist.id)
        get_globals = ChecklistItem.objects.all().filter(global_item=True)
        for item in get_globals:
            ChecklistItem.objects.create(checklist=get_checklist,item=item.item)


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

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Agreement")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectAgreementUpdate, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        check_form_type = ProjectAgreement.objects.get(id=self.kwargs['pk'])

        if check_form_type.short == True:
            form_class = ProjectAgreementSimpleForm
        else:
            form_class = ProjectAgreementForm

        return form_class(**self.get_form_kwargs())


    def get_context_data(self, **kwargs):
        context = super(ProjectAgreementUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})
        context.update({'program': pk})
        getAgreement = ProjectAgreement.objects.get(id=self.kwargs['pk'])
        context.update({'p_agreement': getAgreement.project_name})
        context.update({'p_agreement_program': getAgreement.program})


        try:
            getQuantitative = CollectedData.objects.all().filter(agreement__id=self.kwargs['pk']).order_by('indicator')
        except CollectedData.DoesNotExist:
            getQuantitative = None
        context.update({'getQuantitative': getQuantitative})

        try:
            getMonitor = Monitor.objects.all().filter(agreement__id=self.kwargs['pk']).order_by('type')
        except Monitor.DoesNotExist:
            getMonitor = None
        context.update({'getMonitor': getMonitor})

        try:
            getBenchmark = Benchmarks.objects.all().filter(agreement__id=self.kwargs['pk']).order_by('description')
        except Benchmarks.DoesNotExist:
            getBenchmark = None
        context.update({'getBenchmark': getBenchmark})

        try:
            getBudget = Budget.objects.all().filter(agreement__id=self.kwargs['pk']).order_by('description_of_contribution')
        except Budget.DoesNotExist:
            getBudget = None
        context.update({'getBudget': getBudget})

        try:
            getDocuments = Documentation.objects.all().filter(project__id=self.kwargs['pk']).order_by('name')
        except Documentation.DoesNotExist:
            getDocuments = None
        context.update({'getDocuments': getDocuments})

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

        #get the approval status of the form before it was submitted and set vars for use in condtions
        check_agreement_status = ProjectAgreement.objects.get(id=str(self.kwargs['pk']))
        is_approved = str(form.instance.approval)
        getProgram = Program.objects.get(agreement__id=check_agreement_status.id)
        country = getProgram.country

        #convert form field unicode project name to ascii safe string for email content

        project_name = unicodedata.normalize('NFKD', form.instance.project_name).encode('ascii','ignore')
        #check to see if the approval status has changed
        if str(is_approved) == "approved" and check_agreement_status.approval != "approved":
            budget = form.instance.total_estimated_budget
            if getProgram.budget_check == True:
                try:
                    user_budget_approval = ApprovalAuthority.objects.get(approval_user__user=self.request.user)
                except ApprovalAuthority.DoesNotExist:
                    user_budget_approval = None
            #compare budget amount to users approval amounts

            if getProgram.budget_check:
                if not user_budget_approval or int(budget) > int(user_budget_approval.budget_limit):
                    messages.success(self.request, 'You do not appear to have permissions to approve this initiation')
                    form.instance.approval = 'awaiting approval'
                else:
                    messages.success(self.request, 'Success, Initiation and Budget Approved')
                    form.instance.approval = 'approved'
            else:
                messages.success(self.request, 'Success, Initiation Approved')
                form.instance.approval = 'approved'

            if form.instance.approval == 'approved':
                #email the approver group so they know this was approved
                link = "Link: " + "https://" + get_current_site(self.request).name + "/workflow/projectagreement_detail/" + str(self.kwargs['pk']) + "/"
                subject = "Project Initiation Approved: " + project_name
                message = "A new initiation was approved by " + str(self.request.user) + "\n" + "Budget Amount: " + str(form.instance.total_estimated_budget) + "\n"
                getSubmiter = User.objects.get(username=self.request.user)
                emailGroup(submiter=getSubmiter.email, country=country,group=form.instance.approved_by,link=link,subject=subject,message=message)
        elif str(is_approved) == "awaiting approval" and check_agreement_status.approval != "awaiting approval":
            messages.success(self.request, 'Success, Initiation has been saved and is now Awaiting Approval (Notifications have been Sent)')
            #email the approver group so they know this was approved
            link = "Link: " + "https://" + get_current_site(self.request).name + "/workflow/projectagreement_detail/" + str(self.kwargs['pk']) + "/"
            subject = "Project Initiation Waiting for Approval: " + project_name
            message = "A new initiation was submitted for approval by " + str(self.request.user) + "\n" + "Budget Amount: " + str(form.instance.total_estimated_budget) + "\n"
            emailGroup(country=country,group=form.instance.approved_by,link=link,subject=subject,message=message)
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
        context = super(ProjectAgreementDetail, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context.update({'id': self.kwargs['pk']})

        try:
            getMonitor = Monitor.objects.all().filter(agreement__id=self.kwargs['pk'])
        except Monitor.DoesNotExist:
            getMonitor = None
        context.update({'getMonitor': getMonitor})

        try:
            getBenchmark = Benchmarks.objects.all().filter(agreement__id=self.kwargs['pk'])
        except Benchmarks.DoesNotExist:
            getBenchmark = None
        context.update({'getBenchmarks': getBenchmark})

        try:
            getBudget = Budget.objects.all().filter(agreement__id=self.kwargs['pk'])
        except Budget.DoesNotExist:
            getBudget = None
        context.update({'getBudget': getBudget})

        try:
            getDocuments = Documentation.objects.all().filter(project__id=self.kwargs['pk']).order_by('name')
        except Documentation.DoesNotExist:
            getDocuments = None
        context.update({'getDocuments': getDocuments})

        try:
            getQuantitativeOutputs = CollectedData.objects.all().filter(agreement__id=self.kwargs['pk'])

        except CollectedData.DoesNotExist:
            getQuantitativeOutputs = None
        context.update({'getQuantitativeOutputs': getQuantitativeOutputs})

        return context


class ProjectAgreementDelete(DeleteView):
    """
    Project Agreement Delete
    """
    model = ProjectAgreement
    success_url = '/workflow/dashboard/0/'

    @method_decorator(group_required('Country',url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectAgreementDelete, self).dispatch(request, *args, **kwargs)

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
        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)

        if int(self.kwargs['pk']) == 0:
            getDashboard = ProjectComplete.objects.all().filter(program__country__in=countries)
            return render(request, self.template_name, {'getDashboard':getDashboard,'getPrograms':getPrograms})
        else:
            getDashboard = ProjectComplete.objects.all().filter(program__id=self.kwargs['pk'])
            getProgram =Program.objects.get(id=self.kwargs['pk'])

            return render(request, self.template_name, {'getProgram': getProgram, 'getDashboard':getDashboard,'getPrograms':getPrograms})


class ProjectCompleteCreate(CreateView):
    """
    Project Complete Form
    """
    model = ProjectComplete
    template_name = 'workflow/projectcomplete_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Complete")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectCompleteCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProjectCompleteCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    #get shared data from project agreement and pre-populate form with it
    def get_initial(self):
        getProjectAgreement = ProjectAgreement.objects.get(id=self.kwargs['pk'])
        initial = {
            'approved_by': self.request.user,
            'approval_submitted_by': self.request.user,
            'program': getProjectAgreement.program,
            'office': getProjectAgreement.office,
            'sector': getProjectAgreement.sector,
            'project_agreement': getProjectAgreement.id,
            'project_name': getProjectAgreement.project_name,
            'activity_code': getProjectAgreement.activity_code,
            'expected_start_date': getProjectAgreement.expected_start_date,
            'expected_end_date': getProjectAgreement.expected_end_date,
            'expected_duration': getProjectAgreement.expected_duration,
            'estimated_budget': getProjectAgreement.total_estimated_budget,
            'short': getProjectAgreement.short,
        }

        try:
            getSites = SiteProfile.objects.filter(projectagreement__id=getProjectAgreement.id).values_list('id', flat=True)
            site = {'site': [o for o in getSites] }
            initial['site'] = getSites

        except SiteProfile.DoesNotExist:
            getSites = None

        try:
            getStakeholder = Stakeholder.objects.filter(projectagreement__id=getProjectAgreement.id).values_list('id',flat=True)
            stakeholder = {'stakeholder': [o for o in getStakeholder], }
            initial['stakeholder'] = stakeholder
        except Stakeholder.DoesNotExist:
            getStakeholder = None

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
        getComplete = ProjectComplete.objects.get(id=latest.id)
        getAgreement = ProjectAgreement.objects.get(id=self.request.POST['project_agreement'])

        #update the quantitative data fields to include the newly created complete
        CollectedData.objects.filter(agreement__id=getComplete.project_agreement_id).update(complete=getComplete)

        #update the other budget items
        Budget.objects.filter(agreement__id=getComplete.project_agreement_id).update(complete=getComplete)

        #update the benchmarks
        Benchmarks.objects.filter(agreement__id=getComplete.project_agreement_id).update(complete=getComplete)

        #update main compelte fields
        ProjectComplete.objects.filter(id=getComplete.id).update(account_code=getAgreement.account_code, lin_code=getAgreement.lin_code)

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

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Complete")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ProjectCompleteUpdate, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        check_form_type = ProjectComplete.objects.get(id=self.kwargs['pk'])

        if check_form_type.project_agreement.short == True:
            form_class = ProjectCompleteSimpleForm
        else:
            form_class = ProjectCompleteForm

        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(ProjectCompleteUpdate, self).get_context_data(**kwargs)
        getComplete = ProjectComplete.objects.get(id=self.kwargs['pk'])
        #id = getComplete.project_agreement_id

        context.update({'id': getComplete.pk})
        context.update({'p_name': getComplete.project_name})
        context.update({'p_complete_program': getComplete.program})
        pk = self.kwargs['pk']
        context.update({'pk': pk})
        context.update({'project_id':getComplete.project_agreement_id})

        # get budget data
        try:
            getBudget = Budget.objects.all().filter(Q(agreement__id=getComplete.project_agreement_id) | Q(complete__id=getComplete.pk))
        except Budget.DoesNotExist:
            getBudget = None
        context.update({'getBudget': getBudget})

        # get Quantitative data
        try:
            getQuantitative = CollectedData.objects.all().filter(Q(agreement__id=getComplete.project_agreement_id) | Q(complete__id=getComplete.pk)).order_by('indicator')
        except CollectedData.DoesNotExist:
            getQuantitative = None
        context.update({'getQuantitative': getQuantitative})

        # get benchmark or project components
        try:
            getBenchmark = Benchmarks.objects.all().filter(Q(agreement__id=getComplete.project_agreement_id) | Q(complete__id=getComplete.pk)).order_by('description')
        except Benchmarks.DoesNotExist:
            getBenchmark = None
        context.update({'getBenchmark': getBenchmark})

        # get documents from the original agreement (documents are not seperate in complete)
        try:
            getDocuments = Documentation.objects.all().filter(project__id=getComplete.project_agreement_id).order_by('name')
        except Documentation.DoesNotExist:
            getDocuments = None
        context.update({'getDocuments': getDocuments})


        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ProjectCompleteUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    #get shared data from project agreement and pre-populate form with it
    def get_initial(self):
        initial = {
            'approved_by': self.request.user,
            'approval_submitted_by': self.request.user,
        }

        #update budget with new agreement
        try:
            getBudget = Budget.objects.all().filter(complete_id=self.kwargs['pk'])
            #if there aren't any budget try importing from the agreement
            if not getBudget:
                getComplete = ProjectComplete.objects.get(id=self.kwargs['pk'])
                Budget.objects.filter(agreement=getComplete.project_agreement_id).update(complete_id=self.kwargs['pk'])
        except Budget.DoesNotExist:
            getBudget = None

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

        context.update({'id':self.kwargs['pk']})

        try:
            q_list = [Q(agreement__id=self.kwargs['pk'])]
            if self.get_object():
                q_list.append(Q(complete__id=self.get_object().pk))
            getBenchmark = Benchmarks.objects.filter(reduce(operator.or_, q_list))
        except Benchmarks.DoesNotExist:
            getBenchmark = None

        q_list = [Q(agreement__id=self.kwargs['pk']) ]
        if self.get_object():
            q_list.append( Q(complete__id=self.get_object().pk))
        budgetContribs = Budget.objects.filter(reduce(operator.or_, q_list))

        context['budgetContribs'] = budgetContribs
        context['getBenchmarks'] =  getBenchmark

        return context


class ProjectCompleteDelete(DeleteView):
    """
    Project Complete Delete
    """
    model = ProjectComplete
    success_url = '/workflow/projectcomplete_list/0/'

    @method_decorator(group_required('Country',url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectCompleteDelete, self).dispatch(request, *args, **kwargs)

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
        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)

        if int(self.kwargs['program']) != 0 & int(self.kwargs['project']) == 0:
            getDocumentation = Documentation.objects.all().prefetch_related('program','project').filter(program__id=self.kwargs['program'])
        elif int(self.kwargs['project']) != 0:
            getDocumentation = Documentation.objects.all().prefetch_related('program','project').filter(project__id=self.kwargs['project'])
        else:
            countries = getCountry(request.user)
            getDocumentation = Documentation.objects.all().prefetch_related('program','project','project__office').filter(program__country__in=countries)

        return render(request, self.template_name, {'getPrograms': getPrograms, 'getDocumentation':getDocumentation, 'project_agreement_id': project_agreement_id})


class DocumentationAgreementList(AjaxableResponseMixin, CreateView):
    """
       Documentation Modal List
    """
    model = Documentation
    template_name = 'workflow/documentation_popup_list.html'

    def get(self, request, *args, **kwargs):

        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)

        getDocumentation = Documentation.objects.all().prefetch_related('program', 'project')


        return render(request, self.template_name, {'getPrograms': getPrograms, 'getDocumentation': getDocumentation})


class DocumentationAgreementCreate(AjaxableResponseMixin, CreateView):
    """
    Documentation Form
    """
    model = Documentation
    template_name = 'workflow/documentation_popup_form.html'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Documentation")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DocumentationAgreementCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DocumentationAgreementCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DocumentationAgreementCreate, self).get_context_data(**kwargs)
        getProject = ProjectAgreement.objects.get(id=self.kwargs['id'])
        context.update({'program': getProject.program})
        context.update({'project': getProject})
        context.update({'id': self.kwargs['id']})
        return context

    def get_initial(self):
        getProject = ProjectAgreement.objects.get(id=self.kwargs['id'])
        initial = {
            'project': self.kwargs['id'],
            'program': getProject.program,
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
        context = super(DocumentationAgreementUpdate, self).get_context_data(**kwargs)
        getProject = ProjectAgreement.objects.get(id=self.kwargs['id'])
        context.update({'project': getProject})
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
        context = super(DocumentationAgreementDelete, self).get_context_data(**kwargs)
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

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Documentation")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DocumentationCreate, self).dispatch(request, *args, **kwargs)

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

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Documentation")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DocumentationUpdate, self).dispatch(request, *args, **kwargs)

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
        context['site'] = SiteProfile.objects.get(pk=self.kwargs.get('site_id'))
        return context

    def get_queryset(self):
        q = CollectedData.objects.filter(site__id = self.kwargs.get('site_id')).order_by('program', 'indicator')
        return q


class ProjectCompleteBySite(ListView):
    template_name = 'workflow/site_projectcomplete.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super(ProjectCompleteBySite, self).get_context_data(**kwargs)
        context['site'] = SiteProfile.objects.get(pk=self.kwargs.get('site_id'))
        return context

    def get_queryset(self):
        q = ProjectComplete.objects.filter(site__id = self.kwargs.get('site_id')).order_by('program')
        return q


class SiteProfileList(ListView):
    """
    SiteProfile list creates a map and list of sites by user country access and filters
    by either direct link from project or by program dropdown filter
    """
    model = SiteProfile
    template_name = 'workflow/site_profile_list.html'

    def dispatch(self, request, *args, **kwargs):
        if request.GET.has_key('report'):
            template_name = 'workflow/site_profile_report.html'
        else:
            template_name = 'workflow/site_profile_list.html'
        return super(SiteProfileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        activity_id = int(self.kwargs['activity_id'])
        program_id = int(self.kwargs['program_id'])

        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)

        #this date, 3 months ago, a site is considered inactive
        inactiveSite = pytz.UTC.localize(datetime.now()) - relativedelta(months=3)

        #Filter SiteProfile list and map by activity or program
        if activity_id != 0:
            getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(projectagreement__id=activity_id).distinct()
        elif program_id != 0:
            getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(Q(projectagreement__program__id=program_id) | Q(collecteddata__program__id=program_id)).distinct()
        else:
            getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(country__in=countries).distinct()
        if request.method == "GET" and "search" in request.GET:
            """
             fields = ('name', 'office')
            """
            getSiteProfile = SiteProfile.objects.all().filter(Q(country__in=countries), Q(name__contains=request.GET["search"]) | Q(office__name__contains=request.GET["search"]) | Q(type__profile__contains=request.GET['search']) |
                                                            Q(province__name__contains=request.GET["search"]) | Q(district__name__contains=request.GET["search"]) | Q(village__contains=request.GET['search']) |
                                                             Q(projectagreement__project_name__contains=request.GET["search"]) | Q(projectcomplete__project_name__contains=request.GET['search'])).select_related().distinct()
        #paginate site profile list

        default_list = 10 # default number of site profiles per page
        user_list = request.GET.get('user_list') # user defined number of site profiles per page, 10, 20, 30

        if user_list:
            default_list = int(user_list)

        paginator = Paginator(getSiteProfile, default_list)

        page = request.GET.get('page')

        try:
            getSiteProfile = paginator.page(page)
        except PageNotAnInteger:
            getSiteProfile = paginator.page(1)
        except EmptyPage:
            getSiteProfile = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {'inactiveSite':inactiveSite,'default_list':default_list,'getSiteProfile':getSiteProfile,'project_agreement_id': activity_id,'country': countries,'getPrograms':getPrograms, 'form': FilterForm(), 'helper': FilterForm.helper})


class SiteProfileReport(ListView):
    """
    SiteProfile Report filtered by project
    """
    model = SiteProfile
    template_name = 'workflow/site_profile_report.html'

    def get(self, request, *args, **kwargs):
        countries = getCountry(request.user)
        project_agreement_id = self.kwargs['pk']

        if int(self.kwargs['pk']) == 0:
            getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(country__in=countries).filter(status=1)
            getSiteProfileIndicator = SiteProfile.objects.all().prefetch_related('country','district','province').filter(Q(collecteddata__program__country__in=countries)).filter(status=1)
        else:
            getSiteProfile = SiteProfile.objects.all().prefetch_related('country','district','province').filter(projectagreement__id=self.kwargs['pk']).filter(status=1)
            getSiteProfileIndicator = None

        id=self.kwargs['pk']

        return render(request, self.template_name, {'getSiteProfile':getSiteProfile, 'getSiteProfileIndicator':getSiteProfileIndicator,'project_agreement_id': project_agreement_id,'id':id,'country': countries})


class SiteProfileCreate(CreateView):
    """
    Using SiteProfile Form, create a new site profile
    """
    model = SiteProfile

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="SiteProfile")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(SiteProfileCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(SiteProfileCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        countries = getCountry(self.request.user)
        default_country = None
        if countries:
            default_country = countries[0]
        initial = {
            'approved_by': self.request.user,
            'filled_by': self.request.user,
            'country': default_country
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Site Profile Created!')
        latest = SiteProfile.objects.latest('id')
        redirect_url = '/workflow/siteprofile_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = SiteProfileForm


class SiteProfileUpdate(UpdateView):
    """
    SiteProfile Form Update an existing site profile
    """
    model = SiteProfile

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="SiteProfile")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(SiteProfileUpdate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(SiteProfileUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SiteProfileUpdate, self).get_context_data(**kwargs)
        getProjects = ProjectAgreement.objects.all().filter(site__id=self.kwargs['pk'])
        context.update({'getProjects': getProjects})
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

    @method_decorator(group_required('Country',url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(SiteProfileDelete, self).dispatch(request, *args, **kwargs)

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
            getMonitorData = Monitor.objects.all()
        else:
            getMonitorData = Monitor.objects.all().filter(agreement__id=self.kwargs['pk'])

        if int(self.kwargs['pk']) == 0:
            getBenchmarkData = Benchmarks.objects.all()
        else:
            getBenchmarkData = Benchmarks.objects.all().filter(agreement__id=self.kwargs['pk'])

        return render(request, self.template_name, {'getMonitorData': getMonitorData, 'getBenchmarkData': getBenchmarkData,'project_agreement_id': project_agreement_id})


class MonitorCreate(AjaxableResponseMixin,CreateView):
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
            getComplete = ProjectComplete.objects.get(project_agreement__id=self.kwargs['id'])
            kwargs['complete'] = getComplete.id
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
            getComplete = ProjectComplete.objects.get(id=self.kwargs['id'])
            context.update({'p_name': getComplete.project_name})
        except ProjectComplete.DoesNotExist:
            # do nothing
            context = context
        return context

    def get_initial(self):

        if self.request.GET.get('is_it_project_complete_form', None):
            initial = { 'complete': self.kwargs['id'] }
        else:
            initial = { 'agreement': self.kwargs['id'] }

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
        getBenchmark = Benchmarks.objects.all().get(id=self.kwargs['pk'])

        kwargs['request'] = self.request
        kwargs['agreement'] = getBenchmark.agreement.id
        if getBenchmark.complete:
            kwargs['complete'] = getBenchmark.complete.id
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

        stakeholder_id = self.kwargs['pk']
        getStakeholder = None

        try:
            getStakeholder = Stakeholder.objects.get(id=stakeholder_id)

        except Exception, e:
            pass

        if int(self.kwargs['pk']) == 0:
            countries=getCountry(request.user)
            getContacts = Contact.objects.all().filter(country__in=countries)

        else:
            #getContacts = Contact.objects.all().filter(stakeholder__projectagreement=project_agreement_id)
            getContacts = Stakeholder.contact.through.objects.filter(stakeholder_id = stakeholder_id)

        return render(request, self.template_name, {'getContacts': getContacts, 'getStakeholder': getStakeholder})


class ContactCreate(CreateView):
    """
    Contact Form
    """
    model = Contact
    stakeholder_id = None

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
        country = getCountry(self.request.user)[0]
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
        redirect_url = '/workflow/contact_update/' + self.kwargs['stakeholder_id'] + '/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = ContactForm


class ContactUpdate(UpdateView):
    """
    Contact Form
    """
    model = Contact

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Contact")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ContactUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactUpdate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        context.update({'stakeholder_id': self.kwargs['stakeholder_id']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Contact Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = ContactForm


class ContactDelete(DeleteView):
    """
    Benchmark Form
    """
    model = Contact
    success_url = '/workflow/contact_list/0/'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ContactDelete, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactDelete, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        return context

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Contact Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = ContactForm


class StakeholderList(ListView):
    """
    getStakeholders
    """
    model = Stakeholder
    template_name = 'workflow/stakeholder_list.html'

    def get(self, request, *args, **kwargs):
        # Check for project filter
        project_agreement_id = self.kwargs['pk']
        # Check for program filter
        if self.kwargs['program_id']:
            program_id = int(self.kwargs['program_id'])
        else:
            program_id = 0

        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)

        countries = getCountry(request.user)

        if program_id != 0:
            getStakeholders = Stakeholder.objects.all().filter(projectagreement__program__id=program_id).distinct()

        elif int(self.kwargs['pk']) != 0:
            getStakeholders = Stakeholder.objects.all().filter(projectagreement=self.kwargs['pk']).distinct()

        else:
            getStakeholders = Stakeholder.objects.all().filter(country__in=countries)

        return render(request, self.template_name, {'getStakeholders': getStakeholders, 'project_agreement_id': project_agreement_id,'program_id':program_id, 'getPrograms': getPrograms})


class StakeholderCreate(CreateView):
    """
    Stakeholder Form
    """
    model = Stakeholder

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Stakeholder")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(StakeholderCreate, self).dispatch(request, *args, **kwargs)

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

        country = getCountry(self.request.user)[0]

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

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Stakeholder")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(StakeholderUpdate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(StakeholderUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(StakeholderUpdate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
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
        context = super(QuantitativeOutputsCreate, self).get_context_data(**kwargs)
        is_it_project_complete_form = self.request.GET.get('is_it_project_complete_form', None) or \
            self.request.POST.get('is_it_project_complete_form', None)
        if is_it_project_complete_form == 'true':
            getProgram = Program.objects.get(complete__id = self.kwargs['id'])
        else:
            getProgram = Program.objects.get(agreement__id = self.kwargs['id'])
        context.update({'id': self.kwargs['id']})
        context.update({'program': getProgram})
        return context

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(QuantitativeOutputsCreate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        getProgram = None
        is_it_project_complete_form = self.request.GET.get('is_it_project_complete_form', None) or \
            self.request.POST.get('is_it_project_complete_form', None)

        if is_it_project_complete_form == 'true':
            getProgram = Program.objects.get(complete__id = self.kwargs['id'])
            initial = {
                'complete': self.kwargs['id'],
                'program': getProgram.id,
                'is_it_project_complete_form': 'true',
            }
        else:
            getProgram = Program.objects.get(agreement__id = self.kwargs['id'])
            initial = {
                'agreement': self.kwargs['id'],
                'program': getProgram.id,
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
        return super(QuantitativeOutputsUpdate, self).dispatch(request, *args, **kwargs)


    def get_initial(self):
        """
        get the program to filter the list and indicators by.. the FK to colelcteddata is i_program
        we should change that name at somepoint as it is very confusing
        """
        getProgram = Program.objects.get(i_program__pk=self.kwargs['pk'])
        # indicator = Indicator.objects.get(id)
        is_it_project_complete_form = self.request.GET.get('is_it_project_complete_form', None) or \
            self.request.POST.get('is_it_project_complete_form', None)

        initial = {
            'program': getProgram.id,
            'is_it_project_complete_form': 'true' if is_it_project_complete_form else 'false',
            }
        return initial

    def get_context_data(self, **kwargs):
        context = super(QuantitativeOutputsUpdate, self).get_context_data(**kwargs)
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
        return super(QuantitativeOutputsDelete, self).dispatch(request, *args, **kwargs)

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
            getBudget = Budget.objects.all()
        else:
            getBudget = Budget.objects.all().filter(project_agreement_id=self.kwargs['pk'])

        return render(request, self.template_name, {'getBudget': getBudget, 'project_agreement_id': project_agreement_id})


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
            getChecklist = ChecklistItem.objects.all()
        else:
            getChecklist = ChecklistItem.objects.all().filter(checklist__agreement_id=self.kwargs['pk'])

        return render(request, self.template_name, {'getChecklist': getChecklist, 'project_agreement_id': self.kwargs['pk']})


class ChecklistItemCreate(CreateView):
    """
    Checklist Form
    """
    model = ChecklistItem

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="ChecklistItem")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ChecklistItemCreate, self).dispatch(request, *args, **kwargs)

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
        return super(ChecklistItemCreate, self).dispatch(request, *args, **kwargs)

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

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="ChecklistItem")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ChecklistItemUpdate, self).dispatch(request, *args, **kwargs)

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


def checklist_update_link(AjaxableResponseMixin,pk,type,value):
    """
    Checklist Update from Link
    """
    value = int(value)

    if type == "in_file":
        update = ChecklistItem.objects.filter(id=pk).update(in_file=value)
    elif type == "not_applicable":
        update = ChecklistItem.objects.filter(id=pk).update(not_applicable=value)

    return HttpResponse(value)


class ChecklistItemDelete(DeleteView):
    """
    Checklist Delete
    """
    model = ChecklistItem
    success_url = '/'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(ChecklistItemDelete, self).dispatch(request, *args, **kwargs)

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

        countries=getCountry(request.user)

        if int(self.kwargs['pk']) != 0:
            getAgreements = ProjectAgreement.objects.all().filter(program__id=self.kwargs['pk'])

        elif self.kwargs['status'] != 'none':
            getAgreements = ProjectAgreement.objects.all().filter(approval=self.kwargs['status'])
        else:
            getAgreements = ProjectAgreement.objects.select_related().filter(program__country__in=countries)

        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries).distinct()

        filtered = ProjectAgreementFilter(request.GET, queryset=getAgreements)
        table = ProjectAgreementTable(filtered.queryset)
        table.paginate(page=request.GET.get('page', 1), per_page=20)

        if request.method == "GET" and "search" in request.GET:
            #list1 = list()
            #for obj in filtered:
            #    list1.append(obj)
            """
             fields = 'program','community'
            """
            getAgreements = ProjectAgreement.objects.filter(
                                               Q(project_name__contains=request.GET["search"]) |
                                               Q(activity_code__contains=request.GET["search"]))


        if request.GET.get('export'):
            dataset = ProjectAgreementResource().export(getAgreements)
            response = HttpResponse(dataset.csv, content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename=activity_report.csv'
            return response


        # send the keys and vars
        return render(request, "workflow/report.html", {'country': countries, 'form': FilterForm(), 'filter': filtered, 'helper': FilterForm.helper, 'APPROVALS': APPROVALS, 'getPrograms': getPrograms})


class ReportData(View, AjaxableResponseMixin):
    """
    Render Agreements json object response to the report ajax call
    """

    def get(self, request, *args, **kwargs):

        countries=getCountry(request.user)
        filters = {}
        if int(self.kwargs['pk']) != 0:
            filters['program__id'] = self.kwargs['pk']
        elif self.kwargs['status'] != 'none':
            filters['approval'] = self.kwargs['status']
        else:
            filters['program__country__in'] = countries

        getAgreements = ProjectAgreement.objects.prefetch_related('sectors').select_related('program', 'project_type', 'office', 'estimated_by').filter(**filters).values('id', 'program__id', 'approval', \
                'program__name', 'project_name','site', 'activity_code', 'office__name', \
                'project_name', 'sector__sector', 'project_activity', 'project_type__name', \
                'account_code', 'lin_code','estimated_by__name','total_estimated_budget',\
                'mc_estimated_budget','total_estimated_budget')

        getAgreements = json.dumps(list(getAgreements), cls=DjangoJSONEncoder)

        final_dict = { 'get_agreements': getAgreements }

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
    adminthree = AdminLevelThree.objects.all().filter(district=selected_district)
    adminthree_json = serializers.serialize("json", adminthree)
    return HttpResponse(adminthree_json, content_type="application/json")


def import_service(service_id=1, deserialize=True):
    """
    Import a indicators from a web service (the dig only for now)
    """
    service = ExternalService.objects.all().filter(id=service_id)

    response = requests.get(service.feed_url)
    get_json = json.loads(response.content)

    if deserialize == True:
        data = json.load(get_json) # deserialises it
    else:
    #send json data back not deserialized data
        data = get_json
    #debug the json data string uncomment dump and print
    data2 = json.dumps(data) # json formatted string

    return data


def service_json(request, service):
    """
    For populating service indicators in dropdown
    """
    service_indicators = import_service(service,deserialize=False)
    return HttpResponse(service_indicators, content_type="application/json")


def export_stakeholders_list(request, **kwargs):

    program_id = int(kwargs['program_id'])
    countries = getCountry(request.user)

    if program_id != 0:
        getStakeholders = Stakeholder.objects.prefetch_related('sector').filter(projectagreement__program__id=program_id).distinct()
    else:
        getStakeholders = Stakeholder.objects.prefetch_related('sector').filter(country__in=countries)

    dataset = StakeholderResource().export(getStakeholders)
    response = HttpResponse(dataset.csv, content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=stakeholders.csv'

    return response

def export_sites_list(request, **kwargs):

    #program_id = int(kwargs['program_id'])
    countries = getCountry(request.user)

    #if program_id != 0:
    #    getSites = Sites.objects.prefetch_related('sector').filter(projectagreement__program__id=program_id).distinct()
    #else:
    getSites = SiteProfile.objects.prefetch_related('sector').filter(country__in=countries)

    dataset = SiteProfileResource().export(getSites)
    response = HttpResponse(dataset.csv, content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=sites.csv'

    return response


def save_bookmark(request):
    """
    Create Bookmark from Link
    """
    url = request.POST['url']
    username = request.user
    tola_user = TolaUser.objects.get(user=username)

    TolaBookmarks.objects.create(bookmark_url=url, name=url, user=tola_user)

    return HttpResponse(url)


#Ajax views for single page filtering
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

        countries = getCountry(request.user)

        countries = getCountry(request.user)

        if program_id != 0:
            getStakeholders = Stakeholder.objects.all().filter(projectagreement__program__id=program_id).distinct().values('id', 'create_date', 'type__name', 'name', 'sectors__sector')

        elif int(self.kwargs['pk']) != 0:
            getStakeholders = Stakeholder.objects.all().filter(projectagreement=self.kwargs['pk']).distinct().values('id', 'create_date', 'type__name', 'name', 'sectors__sector')


        else:
            getStakeholders = Stakeholder.objects.all().filter(country__in=countries).values('id', 'create_date', 'type__name', 'name', 'sectors__sector')


        getStakeholders = json.dumps(list(getStakeholders), cls=DjangoJSONEncoder)

        final_dict = {'getStakeholders': getStakeholders}

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

        countries = getCountry(request.user)

        countries = getCountry(request.user)

        if program_id != 0:
            getSites = SiteProfile.objects.all().filter(projectagreement__program__id=program_id).distinct().values('id')

        elif int(self.kwargs['pk']) != 0:
            getSites = SiteProfile.objects.all().filter(projectagreement=self.kwargs['pk']).distinct().values('id')


        else:
            getSites = SiteProfile.objects.all().filter(country__in=countries).values('id')


        getSites = json.dumps(list(getSites), cls=DjangoJSONEncoder)

        final_dict = {'getSites': getSites}

        return JsonResponse(final_dict, safe=False)



class DocumentationListObjects(View, AjaxableResponseMixin):

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['project']
        countries = getCountry(request.user)
        getPrograms = Program.objects.all().filter(funding_status="Funded", country__in=countries)

        if int(self.kwargs['program']) != 0 & int(self.kwargs['project']) == 0:
            getDocumentation = Documentation.objects.all().prefetch_related('program','project').filter(program__id=self.kwargs['program']).values('id', 'name', 'project__project_name', 'create_date')
        elif int(self.kwargs['project']) != 0:
            getDocumentation = Documentation.objects.all().prefetch_related('program','project').filter(project__id=self.kwargs['project']).values('id', 'name', 'project__project_name', 'create_date')
        else:
            countries = getCountry(request.user)
            getDocumentation = Documentation.objects.all().prefetch_related('program','project','project__office').filter(program__country__in=countries).values('id', 'name', 'project__project_name', 'create_date')

        getDocumentation = json.dumps(list(getDocumentation), cls=DjangoJSONEncoder)
        final_dict  = {'getDocumentation': getDocumentation}

        return JsonResponse(final_dict, safe=False)
