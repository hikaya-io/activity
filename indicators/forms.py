#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.urls import reverse_lazy
from django import forms
from django.db.models import Q

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset, Div

from functools import partial
from datetime import datetime

from indicators.models import (
    Indicator, PeriodicTarget, CollectedData, Objective,
    StrategicObjective, ActivityTable, DisaggregationType
)
from workflow.models import Program, SiteProfile, Documentation, \
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
        # widgets = {
        #     'definition': forms.Textarea(attrs={'rows': 4}),
        #     'justification': forms.Textarea(attrs={'rows': 4}),
        #     'quality_assurance': forms.Textarea(attrs={'rows': 4}),
        #     'data_issues': forms.Textarea(attrs={'rows': 4}),
        #     'indicator_changes': forms.Textarea(attrs={'rows': 4}),
        #     'comments': forms.Textarea(attrs={'rows': 4}),
        #     'notes': forms.Textarea(attrs={'rows': 4}),
        #     'rationale_for_target': forms.Textarea(attrs={'rows': 4}),
        # }

    def __init__(self, *args, **kwargs):
        # get the user object to check permissions with
        # print("..................%s..............."
        #   %kwargs.get('targets_sum', 'no targets sum found!!!!') )
        indicator = kwargs.get('instance', None)
        self.request = kwargs.pop('request')
        self.program = kwargs.pop('program')
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
        self.fields['baseline'].widget.attrs['class'] = 'col-sm-4'
        # self.fields['target_frequency_start'].widget = DatePicker.DateInput()
        # self.fields['target_frequency_start'].help_text =
        #   'This field is required'
        # self.fields['target_frequency'].required = False
        self.fields['target_frequency_start'].widget.attrs[
            'class'] = 'monthPicker'
        if self.instance.target_frequency and \
                self.instance.target_frequency != Indicator.LOP:
            self.fields['target_frequency'].widget.attrs['readonly'] = \
                "readonly"
            # self.fields['target_frequency'].widget.attrs['disabled'] =
            # "disabled"
            # self.fields['target_frequency_custom'].widget =
            # forms.HiddenInput()
            # self.fields['target_frequency_start'].widget =
            # forms.HiddenInput()
            # self.fields['target_frequency_num_periods'].widget =
            # forms.HiddenInput()


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

    program2 = forms.CharField(widget=forms.TextInput(
        attrs={'readonly': 'readonly', 'label': 'Program'}))
    indicator2 = forms.CharField(widget=forms.TextInput(
        attrs={'readonly': 'readonly', 'label': 'Indicator'}))
    target_frequency = forms.CharField()
    date_collected = forms.DateField(
        widget=DatePicker.DateInput(), required=True)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.program = kwargs.pop('program')
        self.indicator = kwargs.pop('indicator', None)
        self.activity_table = kwargs.pop('activity_table')
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-4'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.form_action = reverse_lazy('collecteddata_update'
                                               if instance else
                                               'collecteddata_add',
                                               kwargs={'pk': instance.id}
                                               if instance else
                                               {'program': self.program,
                                                'indicator': self.indicator})
        self.helper.form_id = 'collecteddata_update_form'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = True
        self.helper.layout = Layout(
            HTML("""<br/>"""),
            Fieldset('Collected Data',
                     'program', 'program2', 'indicator', 'indicator2',
                     'target_frequency', 'site', 'date_collected',
                     'periodic_target', 'achieved', 'description',

                     ),
            Fieldset('Evidence',
                     'complete', 'evidence', 'activity_table',
                     'update_count_activity_table',
                     HTML("""<a class="output" data-toggle="modal"
                     data-target="#activitytablemodal"
                     href="/indicators/collecteddata_import/">
                     Import Evidence From Activity Tables</a>"""),

                     ),

            Div(
                HTML("""<br/>
    {% if get_disaggregation_label_standard and not
            get_disaggregation_value_standard %}
        <div class='panel panel-default'>
            <!-- Default panel contents -->
            <div class='panel-heading'>Standard Disaggregations</div>
              <!-- Table -->
              <table class="table">
                <tr>
                <th>Disaggregation Level</th>
                <th>Actuals</th>
                </tr>
                {% for item in get_disaggregation_label_standard %}
                <tr>
                    <td>{{ item.label }}</td>
                    <td><input type="text" name="{{ item.id }}" value=""></td>
                </tr>
                {% endfor %}
              </table>
        </div>
    {% else %}
        {% if not get_disaggregation_value_standard %}
            <h4>Standard Disaggregation Levels Not Entered</h4>
            <p>Standard disaggregations are entered in the administrator for
            the entire organizations.  If you are not seeing
            any here, please contact your system administrator.</p>
        {% endif %}
    {% endif %}
    {% if get_disaggregation_label_standard and not get_disaggregation_value %}
        <div class='panel panel-default'>
            <!-- Default panel contents -->
            <div class='panel-heading'>New Disaggregations</div>
              <!-- Table -->
              <table class="table">
                <tr>
                <th>Disaggregation Level</th>
                <th>Actuals</th>
                </tr>
                {% for item in get_disaggregation_label %}
                <tr>
                    <td>{{ item.label }}</td>
                    <td><input type="text" name="{{ item.id }}" value=""></td>
                </tr>
                {% endfor %}
              </table>
        </div>
    {% else %}
        {% if not get_disaggregation_value %}
            <h4>Disaggregation Levels Not Entered For This Indicator</h4>
            <a href="/indicators/indicator_update/{{ indicator_id }}">
            Add a Disaggregation</a>
        {% endif %}
    {% endif %}

    {% if get_disaggregation_value %}
        <div class='panel panel-default'>
            <!-- Default panel contents -->
            <div class='panel-heading'>Existing Disaggregations</div>

              <!-- Table -->
              <table class="table">
                <tr>
                <th>Disaggregation Level</th>
                <th>Actuals</th>
                </tr>
                {% for item in get_disaggregation_value %}
                <tr>
                    <td>{{ item.disaggregation_label.label }}</td>
                    <td><input type="text"
                    name="{{ item.disaggregation_label.id }}"
                    value="{{ item.value }}"></td>
                </tr>
                {% endfor %}
              </table>

        </div>
    {% endif %}

    {% if get_disaggregation_value_standard %}
        <div class='panel panel-default'>
            <!-- Default panel contents -->
            <div class='panel-heading'>Existing Standard Disaggregations</div>

              <!-- Table -->
              <table class="table">
                <tr>
                <th>Disaggregation Level</th>
                <th>Actuals</th>
                </tr>
                {% for item in get_disaggregation_value_standard %}
                <tr>
                    <td>{{ item.disaggregation_label.label }}</td>
                    <td><input type="text"
                    name="{{ item.disaggregation_label.id }}"
                    value="{{ item.value }}"></td>
                </tr>
                {% endfor %}
              </table>

        </div>
    {% endif %}
                """)),
            HTML("""<br/>"""),
            FormActions(
                Submit('submit', 'Save', css_class='btn-success'),
                Reset('reset', 'Reset', css_class='btn-warning')
            )
        )

        super(CollectedDataForm, self).__init__(*args, **kwargs)

        # override the program queryset to use request.user for country
        self.fields['evidence'].queryset = Documentation.objects.filter(
            program=self.program)

        # override the program queryset to use request.user for country
        self.fields['complete'].queryset = ProjectComplete.objects.filter(
            program=self.program)
        self.fields['complete'].label = "Project"

        # override the program queryset to use request.user for country
        countries = get_country(self.request.user)
        # self.fields['program'].queryset = Program.objects\
        #   .filter(funding_status="Funded", country__in=countries).distinct()
        try:
            int(self.program)
            self.program = Program.objects.get(id=self.program)
        except TypeError:
            pass

        self.fields['periodic_target'].queryset = PeriodicTarget.objects\
            .filter(indicator=self.indicator)\
            .order_by('customsort', 'create_date', 'period')

        self.fields['program2'].initial = self.program
        self.fields['program2'].label = "Program"

        try:
            int(self.indicator)
            self.indicator = Indicator.objects.get(id=self.indicator)
        except TypeError as e:
            pass

        self.fields['indicator2'].initial = self.indicator.name
        self.fields['indicator2'].label = "Indicator"
        self.fields['program'].widget = forms.HiddenInput()
        self.fields['indicator'].widget = forms.HiddenInput()
        self.fields['target_frequency'].initial = \
            self.indicator.target_frequency
        self.fields['target_frequency'].widget = forms.HiddenInput()
        # override the program queryset to use request.user for country
        self.fields['site'].queryset = SiteProfile.objects.filter(
            country__in=countries)

        # self.fields['indicator'].queryset = Indicator.objects\
        #   .filter(name__isnull=False, program__country__in=countries)
        self.fields['activity_table'].queryset = ActivityTable.objects.filter(
            Q(owner=self.request.user) | Q(id=self.activity_table))
        self.fields['periodic_target'].label = 'Measure against target*'
        self.fields['achieved'].label = 'Actual value'
        self.fields['date_collected'].help_text = ' '


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
