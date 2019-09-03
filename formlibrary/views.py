#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from .models import TrainingAttendance, Beneficiary, Distribution
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .forms import TrainingAttendanceForm, BeneficiaryForm, DistributionForm
from workflow.models import FormGuidance, Program, ProjectAgreement
from django.utils.decorators import method_decorator
from activity.util import get_country, group_excluded

from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.generic.detail import View
from .mixins import AjaxableResponseMixin
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict


class TrainingList(ListView):
    """
    Training Attendance
    """
    model = TrainingAttendance
    template_name = 'formlibrary/training_list.html'

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['project']
        get_programs = Program.objects.all().filter(
            organization=request.user.activity_user.organization).distinct()

        get_projects = ProjectAgreement.objects.filter(
            program__organization=request.user.activity_user.organization).distinct()

        get_training = TrainingAttendance.objects.all().filter(
            program__organization=request.user.activity_user.organization)

        # filter by program
        if int(self.kwargs['program']) != 0:
            get_training = TrainingAttendance.objects.all().filter(
                program_id=self.kwargs['program'])

        # filter by projects
        if int(self.kwargs['project']) != 0:
            get_training = TrainingAttendance.objects.all().filter(
                project_agreement_id=self.kwargs['program'])

        return render(request, self.template_name, {
            'get_training': get_training,
            'project_agreement_id': project_agreement_id,
            'form_component': 'training_list',
            'get_programs': get_programs,
            'get_projects': get_projects,
            'active': ['forms', 'training_list']
        })


class TrainingCreate(CreateView):
    """
    Training Form
    """
    model = TrainingAttendance
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Training")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(TrainingCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(TrainingCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TrainingCreate, self).get_context_data(**kwargs)
        context['form_title'] = 'Training Attendance Create Form'
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
        messages.success(self.request, 'Success, Training Created!')
        redirect_url = '/formlibrary/training_list/0/0/'
        return HttpResponseRedirect(redirect_url)

    form_class = TrainingAttendanceForm


class TrainingUpdate(UpdateView):
    """
    Training Form
    """
    model = TrainingAttendance
    success_url = '/formlibrary/training_list/0/0/'
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Training")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(TrainingUpdate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(TrainingUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Training Updated!')
        redirect_url = '/formlibrary/training_list/0/0/'
        return HttpResponseRedirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super(TrainingUpdate, self).get_context_data(**kwargs)
        training = TrainingAttendance.objects.get(pk=int(self.kwargs['pk']))
        context['training_name'] = training.training_name
        context['form_title'] = 'Training Attendance Update Form'
        return context

    form_class = TrainingAttendanceForm


def delete_training(request, pk):
    """
    Delete distribution
    """
    distribution = TrainingAttendance.objects.get(pk=int(pk))
    distribution.delete()
    return redirect('/formlibrary/training_list/0/0/')


class BeneficiaryList(ListView):
    """
    Beneficiary
    """
    model = Beneficiary
    template_name = 'formlibrary/beneficiary_list.html'

    def get(self, request, *args, **kwargs):

        program_id = self.kwargs['program']
        training_id = self.kwargs['training']

        organization = request.user.activity_user.organization
        get_programs = Program.objects.all().filter(organization=organization)

        get_training = TrainingAttendance.objects.filter(
            program__in=get_programs)
        get_beneficiaries = Beneficiary.objects.all().filter(program__in=get_programs)

        if int(program_id) != 0:
            get_beneficiaries = Beneficiary.objects.all().filter(
                program__id__contains=program_id)
        if int(training_id) != 0:
            get_beneficiaries = Beneficiary.objects.all().filter(
                training__id=int(training_id))

        return render(request, self.template_name,
                      {
                          'get_beneficiaries': get_beneficiaries,
                          'program_id': program_id,
                          'get_programs': get_programs,
                          'get_training': get_training,
                          'form_component': 'beneficiary_list',
                          'active': ['forms', 'beneficiary_list']
                      })


class BeneficiaryCreate(CreateView):
    """
    Beneficiary Form
    """
    model = Beneficiary
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Beneficiary")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BeneficiaryCreate, self).dispatch(
            request, *args, **kwargs)

    def get_initial(self):
        organization = self.request.user.activity_user.organization
        initial = {
            # 'training': self.kwargs['id'],
            "program": Program.objects.filter(
                organization=organization).first()
        }

        return initial

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BeneficiaryCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        return HttpResponse({'success': True})

    form_class = BeneficiaryForm


class BeneficiaryUpdate(UpdateView):
    """
    Training Form
    """
    model = Beneficiary
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Beneficiary")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BeneficiaryUpdate, self).dispatch(
            request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BeneficiaryUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BeneficiaryUpdate, self).get_context_data(**kwargs)
        beneficiary = Beneficiary.objects.get(pk=int(self.kwargs['pk']))
        context['beneficiary_name'] = beneficiary.beneficiary_name
        context['form_title'] = 'Beneficiary Update Form'
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Beneficiary Updated!')

        return redirect('/formlibrary/beneficiary_list/0/0/')

    form_class = BeneficiaryForm


def delete_beneficiary(request, pk):
    beneficiary = Beneficiary.objects.get(pk=int(pk))
    beneficiary.delete()

    return redirect('/formlibrary/beneficiary_list/0/0/')


class DistributionList(ListView):
    """
    Distribution
    """
    model = Distribution
    template_name = 'formlibrary/distribution_list.html'

    def get(self, request, *args, **kwargs):

        program_id = self.kwargs['program']
        project_id = self.kwargs['project']
        get_programs = Program.objects.all().filter(
            organization=request.user.activity_user.organization).distinct()

        get_projects = ProjectAgreement.objects.filter(
            program__organization=request.user.activity_user.organization)

        get_distribution = Distribution.objects.all().filter(
            program__organization=request.user.activity_user.organization)

        if int(program_id) != 0:
            get_distribution = Distribution.objects.all().filter(
                program_id=int(program_id))
        if int(project_id) != 0:
            get_distribution = Distribution.objects.all().filter(
                initiation_id=int(program_id))

        return render(request, self.template_name, {
            'get_distribution': get_distribution,
            'program_id': program_id,
            'get_programs': get_programs,
            'get_projects': get_projects,
            'form_component': 'distribution_list',
            'active': ['forms', 'distribution_list']
        })


class DistributionCreate(CreateView):
    """
    Distribution Form
    """
    model = Distribution
    guidance = None
    success_url = '/formlibrary/distribution_list/0/0/'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Distribution")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DistributionCreate, self).dispatch(
            request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DistributionCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = {
            'program': self.kwargs['id']
        }

        return initial

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Distribution Created!')
        latest = Distribution.objects.latest('id')
        redirect_url = '/formlibrary/distribution_list/0/0/'
        return HttpResponseRedirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super(DistributionCreate, self).get_context_data(**kwargs)
        context['form_title'] = 'Distribution Create Form'
        return context
    form_class = DistributionForm


class DistributionUpdate(UpdateView):
    """
    Distribution Form
    """
    model = Distribution
    success_url = '/formlibrary/distribution_list/0/0/'
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Distribution")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DistributionUpdate, self).dispatch(
            request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DistributionUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Distribution Updated!')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(DistributionUpdate, self).get_context_data(**kwargs)
        context['form_title'] = 'Distribution Update Form'
        distribution = Distribution.objects.get(pk=int(self.kwargs['pk']))
        context['distribution_name'] = distribution.distribution_name
        return context
    form_class = DistributionForm


def delete_distribution(request, pk):
    """
    Delete distribution
    """
    distribution = Distribution.objects.get(pk=int(pk))
    distribution.delete()
    return redirect('/formlibrary/distribution_list/0/0/')


class TrainingListObjects(View, AjaxableResponseMixin):

    def get(self, request, *args, **kwargs):

        program_id = int(self.kwargs['program'])
        project_id = int(self.kwargs['project'])
        countries = get_country(request.user)
        if int(self.kwargs['program']) == 0:
            get_training = TrainingAttendance.objects.all().filter(
                program__country__in=countries).values(
                'id', 'create_date',
                'training_name',
                'project_agreement__project_name')
        elif program_id != 0 and project_id == 0:
            get_training = TrainingAttendance.objects.all().filter(
                program=program_id).values(
                'id', 'create_date', 'training_name',
                'project_agreement__project_name')
        else:
            get_training = TrainingAttendance.objects.all().filter(
                program_id=program_id,
                project_agreement_id=project_id).values(
                'id', 'create_date', 'training_name',
                'project_agreement__project_name')

        get_training = json.dumps(list(get_training), cls=DjangoJSONEncoder)

        final_dict = {'get_training': get_training}

        return JsonResponse(final_dict, safe=False)


class BeneficiaryListObjects(View, AjaxableResponseMixin):

    def get(self, request, *args, **kwargs):

        program_id = int(self.kwargs['program'])
        project_id = int(self.kwargs['project'])
        organization = self.request.user.activity_user.organization

        if program_id == 0:
            get_beneficiaries = Beneficiary.objects.all().filter(
                Q(program__organization=organization)) \
                .values('id', 'beneficiary_name', 'create_date')
        elif program_id != 0 and project_id == 0:
            get_beneficiaries = Beneficiary.objects.all().filter(
                program__id=program_id).values('id', 'beneficiary_name',
                                               'create_date')
        else:
            get_beneficiaries = Beneficiary.objects.all().filter(
                program__id=program_id,
                training__project_agreement=project_id).values(
                'id', 'beneficiary_name', 'create_date')

        get_beneficiaries = json.dumps(
            list(get_beneficiaries), cls=DjangoJSONEncoder)

        final_dict = {'get_beneficiaries': get_beneficiaries}

        return JsonResponse(final_dict, safe=False)


class DistributionListObjects(View, AjaxableResponseMixin):

    def get(self, request, *args, **kwargs):

        program_id = int(self.kwargs['program'])
        project_id = int(self.kwargs['project'])
        if program_id == 0:
            get_distribution = Distribution.objects.all().filter(
                program__organization=request.user.activity_user.organization).\
                values('id', 'distribution_name', 'create_date', 'program')
        elif program_id != 0 and project_id == 0:
            get_distribution = Distribution.objects.all().filter(
                program_id=program_id).values(
                'id', 'distribution_name', 'create_date', 'program')
        else:
            get_distribution = Distribution.objects.all().filter(
                program_id=program_id,
                initiation_id=project_id).values('id', 'distribution_name',
                                                 'create_date', 'program')

        get_distribution = json.dumps(
            list(get_distribution), cls=DjangoJSONEncoder)

        final_dict = {'get_distribution': get_distribution}

        return JsonResponse(final_dict, safe=False)


# program and project & training filters
class GetAgreements(View, AjaxableResponseMixin):

    def get(self, request, *args, **kwargs):

        program_id = self.kwargs['program']
        countries = get_country(request.user)
        if program_id != 0:
            get_agreements = ProjectAgreement.objects.all().filter(
                program=program_id).values('id', 'project_name')
        else:
            pass

        final_dict = {}
        if get_agreements:
            get_agreements = json.dumps(
                list(get_agreements), cls=DjangoJSONEncoder)
            final_dict = {'get_agreements': get_agreements}

        return JsonResponse(final_dict, safe=False)


def add_training(request):
    data = {
        'training_name': request.POST.get('training_name'),
        'start_date': request.POST.get('start_date'),
        'end_date': request.POST.get('end_date'),
        'program_id': int(request.POST.get('program')),
    }

    instance = TrainingAttendance.objects.create(**data)

    if instance.id:
        return HttpResponse({'success': True})

    return HttpResponse({'success': False})


def add_distribution(request):
    data = {
        'distribution_name': request.POST.get('distribution_name'),
        'start_date': request.POST.get('start_date'),
        'end_date': request.POST.get('end_date'),
        'program_id': int(request.POST.get('program')),
    }

    instance = Distribution.objects.create(**data)

    if instance.id:
        return HttpResponse({'success': True})

    return HttpResponse({'success': False})
