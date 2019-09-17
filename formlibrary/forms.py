#!/usr/bin/python3
# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Reset
from django import forms
from .models import TrainingAttendance, Distribution, Beneficiary
from workflow.models import Program, ProjectAgreement, Office, Province, SiteProfile
from functools import partial
from activity.util import get_country
from django_select2.forms import Select2MultipleWidget


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
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True

        super(DistributionForm, self).__init__(*args, **kwargs)

        self.fields['initiation'].queryset = ProjectAgreement.objects.filter(
            program__organization=self.request.user.activity_user.organization)
        self.fields['program'].queryset = Program.objects.filter(
            organization=self.request.user.activity_user.organization)
        self.fields['office_code'].queryset = Office.objects.all()
        self.fields['province'].queryset = Province.objects.all()


class BeneficiaryForm(forms.ModelForm):

    class Meta:
        model = Beneficiary
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True

        super(BeneficiaryForm, self).__init__(*args, **kwargs)

        organization = self.request.user.activity_user.organization
        self.fields['training'].queryset = TrainingAttendance.objects.filter(
            program__organization=organization)
        self.fields['program'].queryset = Program.objects.filter(
            organization=organization)
        self.fields['distribution'].queryset = Distribution.objects.filter(
            program__organization=organization)
        self.fields['site'].queryset = SiteProfile.objects.filter(
            organizations__id__contains=self.request.user.activity_user.organization.id)
