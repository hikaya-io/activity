#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from .models import TrainingAttendance, Beneficiary, Distribution
from django.urls import reverse_lazy

from .forms import TrainingAttendanceForm, BeneficiaryForm, DistributionForm
from workflow.models import FormGuidance, Program, ProjectAgreement
from django.utils.decorators import method_decorator
from activity.util import get_country, group_excluded

from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q

from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.detail import View
from .mixins import AjaxableResponseMixin
import json
from django.core.serializers.json import DjangoJSONEncoder


class TrainingList(ListView):
    """
    Training Attendance
    """
    model = TrainingAttendance
    template_name = 'formlibrary/training_list.html'

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['pk']
        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded", country__in=countries).distinct()
        if int(self.kwargs['pk']) == 0:
            get_training = TrainingAttendance.objects.all().filter(
                program__country__in=countries)
        else:
            get_training = TrainingAttendance.objects.all().filter(
                project_agreement_id=self.kwargs['pk'])

        return render(request, self.template_name,
                      {'get_training': get_training,
                       'project_agreement_id': project_agreement_id,
                       'get_programs': get_programs,
                       'active': ['forms', 'training_list']})


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
        latest = TrainingAttendance.objects.latest('id')
        redirect_url = '/formlibrary/training_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = TrainingAttendanceForm


class TrainingUpdate(UpdateView):
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

        return self.render_to_response(self.get_context_data(form=form))

    form_class = TrainingAttendanceForm


class TrainingDelete(DeleteView):
    """
    Training Delete
    """
    model = TrainingAttendance
    success_url = '/formlibrary/training_list/0/'
    template_name = 'formlibrary/training_confirm_delete.html'

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Training Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = TrainingAttendanceForm


class BeneficiaryList(ListView):
    """
    Beneficiary
    """
    model = Beneficiary
    template_name = 'formlibrary/beneficiary_list.html'

    def get(self, request, *args, **kwargs):

        project_agreement_id = self.kwargs['pk']
        organization = request.user.activity_user.organization
        get_programs = Program.objects.all().filter(
            funding_status="Funded", organization=organization).distinct()

        if int(self.kwargs['pk']) == 0:
            get_beneficiaries = Beneficiary.objects.all().filter(
                program__in=get_programs)
        else:
            get_beneficiaries = Beneficiary.objects.all().filter(
                training__id=self.kwargs['pk'])

        return render(request, self.template_name,
                      {'get_beneficiaries': get_beneficiaries,
                       'project_agreement_id': project_agreement_id,
                       'get_programs': get_programs,
                       'active': ['forms', 'beneficiary_list']})


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
        messages.success(self.request, 'Success, Beneficiary Created!')
        latest = Beneficiary.objects.latest('id')
        redirect_url = '/formlibrary/beneficiary_list/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

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

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Beneficiary Updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = BeneficiaryForm


class BeneficiaryDelete(DeleteView):
    """
    Beneficiary Delete
    """
    model = Beneficiary
    success_url = reverse_lazy('beneficiary_list')

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(BeneficiaryDelete, self).dispatch(
            request, *args, **kwargs)

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Beneficiary Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BeneficiaryForm


class DistributionList(ListView):
    """
    Distribution
    """
    model = Distribution
    template_name = 'formlibrary/distribution_list.html'

    def get(self, request, *args, **kwargs):

        program_id = self.kwargs['pk']
        countries = get_country(request.user)
        get_programs = Program.objects.all().filter(
            funding_status="Funded", country__in=countries).distinct()

        if int(self.kwargs['pk']) == 0:
            get_distribution = Distribution.objects.all().filter(
                program__country__in=countries)
        else:
            get_distribution = Distribution.objects.all().filter(
                program_id=self.kwargs['pk'])

        return render(request, self.template_name,
                      {'get_distribution': get_distribution,
                       'program_id': program_id, 'get_programs': get_programs, 'active': ['forms', 'distribution_list']})


class DistributionCreate(CreateView):
    """
    Distribution Form
    """
    model = Distribution
    guidance = None
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
        redirect_url = '/formlibrary/distribution_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = DistributionForm


class DistributionUpdate(UpdateView):
    """
    Distribution Form
    """
    model = Distribution
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

        return self.render_to_response(self.get_context_data(form=form))

    form_class = DistributionForm


class DistributionDelete(DeleteView):
    """
    Distribution Delete
    """
    model = Distribution
    success_url = '/formlibrary/distribution_list/0/'
    template_name = 'formlibrary/distribution_confirm_delete.html'

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Distribution Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DistributionForm

# Ajax views for ajax filters and paginators


class TrainingListObjects(View, AjaxableResponseMixin):

    def get(self, request, *args, **kwargs):

        program_id = int(self.kwargs['program'])
        project_id = int(self.kwargs['project'])
        print(project_id)
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
                Q(program__organization=organization))\
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
        countries = get_country(request.user)
        if program_id == 0:
            get_distribution = Distribution.objects.all().filter(
                program__country__in=countries).values(
                'id', 'distribution_name', 'create_date', 'program')
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
