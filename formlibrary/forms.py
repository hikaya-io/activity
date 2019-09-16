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
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.layout = Layout(
            'training_name',
            Row(
                Column('trainer_name', css_class='form-group col-md-6 mb-0'),
                Column('trainer_contact_num', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('program', css_class='form-group col-md-6 mb-0'),
                Column('project_agreement', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('training_duration', css_class='form-group col-md-6 mb-0'),
                Column('reporting_period', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),

            Row(
                Column('form_filled_by', css_class='form-group col-md-6 mb-0'),
                Column('form_filled_by_contact_num', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-0'),
                Column('end_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('implementer', css_class='form-group col-md-4 mb-0'),
                Column('location', css_class='form-group col-md-4 mb-0'),
                Column('community', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('total_participants', css_class='form-group col-md-4 mb-0'),
                Column('total_male', css_class='form-group col-md-4 mb-0'),
                Column('total_female', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('total_age_0_14_male', css_class='form-group col-md-6 mb-0'),
                Column('total_age_0_14_female', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('total_age_15_24_male', css_class='form-group col-md-6 mb-0'),
                Column('total_age_15_24_female', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('total_age_25_59_male', css_class='form-group col-md-6 mb-0'),
                Column('total_age_25_59_female', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Reset('reset', 'Close', css_class='btn-md btn-close'),
            Submit('submit', 'Save', css_class='btn-md btn-success'), )

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
    training = forms.ModelMultipleChoiceField(
        queryset=TrainingAttendance.objects.all(),
        widget=Select2MultipleWidget,
        required=False
    )

    distribution = forms.ModelMultipleChoiceField(
        queryset=Distribution.objects.all(),
        widget=Select2MultipleWidget,
        required=False
    )

    program = forms.ModelMultipleChoiceField(
        queryset=Program.objects.all(),
        widget=Select2MultipleWidget,
        required=False
    )

    # site = forms.ModelChoiceField(
    #     queryset=SiteProfile.objects.all(),
    #     widget=Select2MultipleWidget,
    #     required=False
    # )

    class Meta:
        model = Beneficiary
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.layout = Layout(
            'beneficiary_name',
            'father_name',
            Row(
                Column('training', css_class='form-group col-md-6 mb-0'),
                Column('distribution', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('age', css_class='form-group col-md-6 mb-0'),
                Column('gender', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('site', css_class='form-group col-md-6 mb-0'),
                Column('program', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'remarks',
            Reset('reset', 'Close', css_class='btn btn-md btn-close'),
            Submit('submit', 'Save', css_class='btn btn-md btn-success'),
        )

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
