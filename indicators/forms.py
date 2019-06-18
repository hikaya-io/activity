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
        widgets = {
            'definition': forms.Textarea(attrs={'rows': 4}),
            'justification': forms.Textarea(attrs={'rows': 4}),
            'quality_assurance': forms.Textarea(attrs={'rows': 4}),
            'data_issues': forms.Textarea(attrs={'rows': 4}),
            'indicator_changes': forms.Textarea(attrs={'rows': 4}),
            'comments': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'rationale_for_target': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        # get the user object to check permissions with
        # print("..................%s..............."
        #   %kwargs.get('targets_sum', 'no targets sum found!!!!') )
        indicator = kwargs.get('instance', None)
        self.request = kwargs.pop('request')
        self.program = kwargs.pop('program')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = reverse_lazy(
            'indicator_update', kwargs={'pk': indicator.id})
        self.helper.form_id = 'indicator_update_form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-4'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = False
        self.helper.layout = Layout(

            TabHolder(
                Tab('Summary',
                    Fieldset('',
                             'program', 'sector', 'objectives',
                             'strategic_objectives',
                             ),
                    HTML("""
                        {% if get_external_service_record %}
                            <div class='panel panel-default'>
                            <div class='panel-heading'>
                            External Indicator Service</div>
                                <table class="table">
                                    <tr>
                                        <th>Service Name</th>
                                        <th>View Guidance</th>
                                    </tr>
                                    {% for item in get_external_service_record %}
                                        <tr>
                                            <td>
                                            {{ item.external_service.name }}
                                            </td>
                                            <td><a target="_new"
                                            href='{{ item.full_url }}'>View</a>
                                        </tr>
                                    {% endfor %}
                                </table>
                            </div>
                        {% endif %}
                    """),
                    ),
                Tab('Performance',
                    Fieldset(
                        '', 'name', 'level', 'number', 'source',
                        'definition', 'justification', 'disaggregation',
                        'indicator_type', PrependedText(
                            'key_performance_indicator', False))),
                Tab('Targets',
                    Fieldset('',
                             'unit_of_measure', 'lop_target',
                             'rationale_for_target',
                             Field('baseline',
                                   template="indicators/crispy.html"),
                             'baseline_na', 'target_frequency',
                             'target_frequency_start',
                             'target_frequency_custom',
                             'target_frequency_num_periods'
                             ),
                    Fieldset('',
                             HTML("""
    <div id="div_id_create_targets_btn" class="form-group">
        <div class="controls col-sm-offset-4 col-sm-6">
            <button type="button" id="id_create_targets_btn"
            class="btn btn-primary">Create targets</button>
            <button type="button" id="id_delete_targets_btn"
            class="btn btn-link">Remove all targets</button>
        </div>
    </div>
                            """)),
                    Fieldset('',
                             HTML("""
    <div id="id_div_periodic_tables_placeholder">
    {% if periodic_targets and indicator.target_frequency != 1%}
        <div class="container-fluid" style="background-color: #F5F5F5;
        margin: 0px -30px 0px -30px;">
            <div class="row">
                <div class="col-sm-offset-2 col-sm-8"
                style="padding-left: 1px; margin-top: 30px;">
                    <h4>{{ indicator.get_target_frequency_label }} targets</h4>
                </div>
            </div>
            <div class="row">
                <div id="periodic-targets-tablediv"
                class="col-sm-offset-2 col-sm-8">
                    <table class="table table-condensed"
                    id="periodic_targets_table" style="margin-bottom: 1px;">
                        <tbody>
                            {% for pt in periodic_targets %}
                                <tr id="{{pt.pk}}"
                                data-collected-count="{{pt.num_data}}"
                                class="periodic-target">
                                    <td style="width:50px;
                                    vertical-align: middle; border: none;">
            <a href="{% url 'pt_delete' pt.id %}" id="deleteLastPT"
            class="detelebtn" style="text-align: center;
                margin: 3px 10px 0px 10px; color:red;
                display:{% if forloop.last and indicator.target_frequency != 2
                    or indicator.target_frequency == 8 %}
                block{% else %}none{% endif %}">
                    <span class="glyphicon glyphicon-remove"></span>
            </a>
                                    </td>
                                    <td style="padding:1px; border:none;
                                    vertical-align:middle;">
                                    {% if indicator.target_frequency == 8 %}
                                        <div class="controls border-1px">
                                            <input type="text"
                                            name="{{ pt.period }}"
                                            value="{{ pt.period }}"
                                                class="form-control
                                                input-text">
                                            <span style="margin:0px;"
                                            class="help-block"> </span>
                                        </div>
                                    {% else %}
                                        <div style="line-height:1;">
                                        <strong>{{ pt.period }}</strong>
                                        </div>
                                        <div style="line-height:1;
                                        margin-top:3px;">
                                        {{ pt.start_date_formatted }}
                                        {% if pt.start_date %} -
                                        {% endif %}
                                        {{ pt.end_date_formatted }}</div>
                                    {% endif %}
                                    </td>
                                    <td align="right" style="padding:1px;
                                    border:none; vertical-align: middle;
                                        width: 150px">
                                            <div class="controls border-1px">
                                                <input type="number"
                                                id="pt-{{ pt.id }}"
                                                name="{{ pt.period }}"
                                    value="{{ pt.target|floatformat:"-2" }}"
                                    data-start-date=
                                "{{pt.start_date|date:"M d, Y"|default:''}}"
                                    data-end-date=
                                    "{{pt.end_date|date:"M d, Y"|default:''}}"
                                    placeholder="Enter target"
                                    class="form-control input-value">
                                    <span id="hint_id_pt_{{pt.pk}}"
                                    style="margin:0px;" class="help-block">
                                                </span>
                                            </div>
                                    </td>
                                </tr>
                                {% if forloop.last %}
                                    <tr id="pt_sum_targets">
                                        <td class="pt-delete-row"
                                        style="border: none;">
                                        </td>
                                        <td align="left"
                                        style="padding-left:0px; border:none;
                                        vertical-align: middle;">
                                            <strong>Sum of targets</strong>
                                        </td>
                                        <td align="right" style="border:none;
                                        vertical-align: middle;">
                                    <div style="margin: 5px 10px;">
                                        <strong><span id="id_span_targets_sum">
                                        {{targets_sum|floatformat:"-2"}}
                                        </span></strong>
                                    </div>
                                        </td>
                                    </tr>
                                {% endif %}
                            {% endfor %}
                            <tr style="background-color:#F5F5F5">
                                <td class="pt-delete-row"
                                style="border: none;">
                                </td>
                                <td align="left" style="padding-left:0px;
                                border:none; vertical-align: middle;">
                                    <strong>Life of Program (LoP) target
                                    </strong>
                                </td>
                                <td align="right" style="border:none;
                                vertical-align: middle;">
                            <div style="margin: 5px 10px;">
                                <strong>
                                {{indicator.lop_target|floatformat:"-2"}}
                                </strong>
                            </div>
                                </td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr style="background-color:#F5F5F5">
                                <td colspan="3" style="color:red; padding: 0px"
                                id="id_pt_errors"></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
            {% if indicator.target_frequency != 2 %}
                <div class="row">
                    <div class="col-sm-offset-2 col-sm-8"
                    style="padding-left: 1px; margin-top:10px;
                    margin-bottom:40px;">
                        <a href="#" id="addNewPeriodicTarget"
                        style="padding-left: 1px;"
                        class="button btn-lg btn-link">
                        <span class=" glyphicon glyphicon-plus-sign"></span>
                         Add a target</a>
                    </div>
                </div>
            {% else %}
                <div class="row" style="height: 30px; margin-bottom: 15px">
                </div>
            {% endif %}
        </div>
    {% endif %}
    </div>
                        """),
                             ),
                    ),
                Tab('Data Acquisition',
                    Fieldset('',
                             'means_of_verification', 'data_collection_method',
                             'data_collection_frequency',
                             'data_points', 'responsible_person',
                             ),
                    ),
                Tab('Analysis and Reporting',
                    Fieldset('',
                             'method_of_analysis', 'information_use',
                             'reporting_frequency', 'quality_assurance',
                             'data_issues', 'indicator_changes', 'comments',
                             'notes'
                             ),
                    ),
                Tab('Approval',
                    Fieldset('',
                             'approval_submitted_by', 'approved_by',
                             ),
                    ),
            ),

            # HTML("""<hr/>"""),
            # FormActions(
            #     Submit('submit', 'Save', css_class='btn-default'),
            #     Reset('reset', 'Reset', css_class='btn-default')
            # )
        )

        super(IndicatorForm, self).__init__(*args, **kwargs)

        # override the program queryset to use request.user for country
        countries = get_country(self.request.user)
        self.fields['program'].queryset = Program.objects.filter(
            funding_status="Funded", country__in=countries)
        self.fields['disaggregation'].queryset = DisaggregationType.objects. \
            filter(country__in=countries).filter(standard=False)
        self.fields['objectives'].queryset = Objective.objects.all().filter(
            program__id__in=self.program)
        self.fields[
            'strategic_objectives'].queryset = StrategicObjective.objects.\
            filter(country__in=countries)
        self.fields['approved_by'].queryset = ActivityUser.objects.filter(
            country__in=countries).distinct()
        self.fields[
            'approval_submitted_by'].queryset = ActivityUser.objects.filter(
            country__in=countries).distinct()
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
