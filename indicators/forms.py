#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.urls import reverse_lazy
from django import forms
from django.db.models import Q

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Submit, Reset, Row, Column
)

from functools import partial
from datetime import datetime

from indicators.models import (
    Indicator, PeriodicTarget, CollectedData, Objective,
    StrategicObjective, ActivityTable, DisaggregationType, Level, IndicatorType, DataCollectionFrequency
)
from workflow.models import Program, Documentation, \
    ProjectComplete, ActivityUser
from activity.util import get_country


class DatePicker(forms.DateInput):
    """
    Use in form to create a Jquery datepicker element
    """
    template_name = 'datepicker.html'

    DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        indicator = kwargs.get('instance', None)
        self.request = kwargs.pop('request')
        self.program = kwargs.pop('program')
        self.organization = kwargs.pop('organization')
        self.program_id = kwargs.pop('program_id')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = reverse_lazy(
            'indicator_update', kwargs={'pk': indicator.id})
        self.helper.form_id = 'indicator_update_form'

        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = False

        super(IndicatorForm, self).__init__(*args, **kwargs)

        # override the program queryset to use request.user for country
        countries = get_country(self.request.user)
        self.fields['program'].queryset = Program.objects.filter(
            organization=self.request.user.activity_user.organization)
        self.fields['disaggregation'].queryset = DisaggregationType.objects.filter(
            country__in=countries).filter(standard=False)
        self.fields['objectives'].queryset = Objective.objects.filter(
            program__id=self.program_id)

        self.fields['approved_by'].queryset = ActivityUser.objects.filter(
            organization=self.request.user.activity_user.organization).distinct()
        self.fields[
            'approval_submitted_by'].queryset = ActivityUser.objects.filter(
            organization=self.request.user.activity_user.organization).distinct()
        self.fields['program'].widget.attrs['readonly'] = "readonly"
        self.fields['target_frequency_start'].widget.attrs[
            'class'] = 'monthPicker'
        self.fields['key_performance_indicator'].label = """Key Performance Indicator for
             this {}""".format(self.organization.level_1_label)
        self.fields['objectives'].label = '{} objective'.format(self.organization.level_1_label)
        self.fields['program'].label = '{}'.format(self.organization.level_1_label)
        self.fields['level'].queryset = Level.objects.filter().order_by('sort', 'id')
        self.fields['indicator_type'].queryset = IndicatorType.objects.filter(
            organization=self.request.user.activity_user.organization).distinct()
        self.fields['data_collection_frequency'].queryset = DataCollectionFrequency.objects.filter(
            organization=self.request.user.activity_user.organization).distinct()


class CollectedDataForm(forms.ModelForm):

    class Meta:
        model = CollectedData
        exclude = ['create_date', 'edit_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_date_collected(self):
        date_collected = self.cleaned_data['date_collected']
        date_collected = datetime.strftime(date_collected, '%Y-%m-%d')
        return date_collected

    target_frequency = forms.CharField()
    date_collected = forms.DateField(
        widget=DatePicker.DateInput(), required=True)

    def __init__(self, *args, **kwargs):
        # instance = kwargs.get('instance', None)
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.program = kwargs.pop('program')
        self.indicator = kwargs.pop('indicator', None)
        self.activity_table = kwargs.pop('activity_table')
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.form_id = 'collecteddata_update_form'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = True

        super(CollectedDataForm, self).__init__(*args, **kwargs)

        # override the program queryset to use request.user for country
        self.fields['evidence'].queryset = Documentation.objects.filter(
            program=self.program)

        # override the program queryset to use request.user for country
        self.fields['complete'].queryset = ProjectComplete.objects.filter(
            program=self.program)
        self.fields['complete'].label = "Project"

        try:
            program_id = int(self.program)
            self.program = Program.objects.filter(id=program_id).first()
        except TypeError:
            pass

        self.fields['periodic_target'].queryset = PeriodicTarget.objects\
            .filter(indicator=self.indicator)\
            .order_by('customsort', 'create_date', 'period')

        try:
            int(self.indicator)
            self.indicator = Indicator.objects.get(id=int(self.indicator))
        except TypeError:
            pass
        self.fields['target_frequency'].required = False

        if self.indicator is not None:
            self.fields['target_frequency'].initial = self.indicator.target_frequency

        self.fields['activity_table'].queryset = ActivityTable.objects.filter(
            Q(owner=self.request.user.activity_user) | Q(id=self.activity_table))
        self.fields['periodic_target'].label = 'Target Period*'
        self.fields['achieved'].label = 'Actual value'
        self.fields['date_collected'].help_text = ' '
        self.fields['evidence'].queryset = Documentation.objects.filter()


class StrategicObjectiveForm(forms.ModelForm):
    class Meta:
        model = StrategicObjective
        exclude = ('create_date', 'edit_date')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.current_objective = kwargs.pop('current_objective')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('parent', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),

            Row(
                Column('description', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Reset('reset', 'Close', css_class='btn-md btn-close'),
            Submit('submit', 'Save Changes', css_class='btn-md btn-success'),
        )
        super(StrategicObjectiveForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = StrategicObjective.objects.\
            filter(organization=self.request.user.activity_user.organization).\
            exclude(pk=self.current_objective.id)


class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = Objective
        exclude = ('create_date', 'edit_date')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.current_objective = kwargs.pop('current_objective')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('parent', css_class='form-group col-md-6 mb-0'),
                Column('program', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),

            Row(
                Column('description', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Reset('reset', 'Close', css_class='btn-md btn-close'),
            Submit('submit', 'Save Changes', css_class='btn-md btn-success'),
        )
        super(ObjectiveForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Objective.objects.\
            filter(program__organization=self.request.user.activity_user.organization).\
            exclude(pk=self.current_objective.id)


class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        exclude = ('create_date', 'edit_date')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Reset('reset', 'Close', css_class='btn-md btn-close'),
            Submit('submit', 'Save Changes', css_class='btn-md btn-success'),
        )
        super(LevelForm, self).__init__(*args, **kwargs)
