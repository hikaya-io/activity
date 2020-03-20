#!/usr/bin/python3
# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from django import forms
from .models import TrainingAttendance, Distribution, Individual
from workflow.models import Program, ProjectAgreement, Office, Province, SiteProfile
from functools import partial


class DatePicker(forms.DateInput):
    """
    Use in form to create a Jquery datepicker element
    """
    template_name = 'datepicker.html'

    DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class TrainingAttendanceForm(forms.ModelForm):
    start_date = forms.DateField(widget=DatePicker.DateInput(), required=False)
    end_date = forms.DateField(widget=DatePicker.DateInput(), required=False)

    class Meta:
        model = TrainingAttendance
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.organization = kwargs.pop('organization')
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True

        super(TrainingAttendanceForm, self).__init__(*args, **kwargs)

        self.fields['project_agreement'].queryset = \
            ProjectAgreement.objects.filter(
                program__organization=self.request.user.activity_user.organization)
        self.fields['program'].queryset = Program.objects.filter(
            organization=self.request.user.activity_user.organization)

        self.fields['training_name'].label = '{} name'.format(self.organization.training_label)
        self.fields['training_duration'].label = '{} duration'.format(self.organization.training_label)


class DistributionForm(forms.ModelForm):

    start_date = forms.DateField(widget=DatePicker.DateInput(), required=False)
    end_date = forms.DateField(widget=DatePicker.DateInput(), required=False)
    form_filled_date = forms.DateField(widget=DatePicker.DateInput(), required=False)
    form_verified_date = forms.DateField(widget=DatePicker.DateInput(), required=False)

    class Meta:
        model = Distribution
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.organization = kwargs.pop('organization')
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True

        super(DistributionForm, self).__init__(*args, **kwargs)

        self.fields['initiation'].queryset = ProjectAgreement.objects.filter(
            program__organization=self.request.user.activity_user.organization)
        self.fields['program'].queryset = Program.objects.filter(
            organization=self.request.user.activity_user.organization)
        self.fields['office_code'].queryset = Office.objects.filter(
            organization=self.request.user.activity_user.organization)
        self.fields['province'].queryset = Province.objects.all()

        self.fields['distribution_name'].label = '{} name'.format(self.organization.distribution_label)
        self.fields['distribution_implementer'].label = '{} implementer'.format(self.organization.distribution_label)
        self.fields['distribution_location'].label = '{} location'.format(self.organization.distribution_label)
        self.fields['distribution_indicator'].label = '{} indicator'.format(self.organization.distribution_label)


class IndividualForm(forms.ModelForm):

    class Meta:
        model = Individual
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.organization = kwargs.pop('organization')
        self.request = kwargs.pop('request')
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True

        super(IndividualForm, self).__init__(*args, **kwargs)

        organization = self.request.user.activity_user.organization
        self.fields['training'].queryset = TrainingAttendance.objects.filter(
            program__organization=organization)
        self.fields['program'].queryset = Program.objects.filter(
            organization=organization)
        self.fields['distribution'].queryset = Distribution.objects.filter(
            program__organization=organization)
        self.fields['site'].queryset = SiteProfile.objects.filter(
            organizations__id__contains=self.request.user.activity_user.organization.id)

        self.fields['beneficiary_name'].label = '{} name'.format(self.organization.beneficiary_label)
