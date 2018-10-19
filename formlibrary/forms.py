from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from .models import TrainingAttendance, Distribution, Beneficiary
from workflow.models import Program, ProjectAgreement, Office, Province, SiteProfile
from functools import partial
from tola.util import getCountry


class DatePicker(forms.DateInput):
    """
    Use in form to create a Jquery datepicker element
    """
    template_name = 'datepicker.html'

    DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class TrainingAttendanceForm(forms.ModelForm):

    class Meta:
        model = TrainingAttendance
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.add_input(Submit('submit', 'Save'))

        super(TrainingAttendanceForm, self).__init__(*args, **kwargs)

        countries = getCountry(self.request.user)
        self.fields['project_agreement'].queryset = ProjectAgreement.objects.filter(program__country__in=countries)
        self.fields['program'].queryset = Program.objects.filter(country__in=countries)


class DistributionForm(forms.ModelForm):

    start_date = forms.DateField(widget=DatePicker.DateInput(), required=False)
    end_date = forms.DateField(widget=DatePicker.DateInput(), required=False)

    class Meta:
        model = Distribution
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.add_input(Submit('submit', 'Save'))

        super(DistributionForm, self).__init__(*args, **kwargs)

        countries = getCountry(self.request.user)
        self.fields['initiation'].queryset = ProjectAgreement.objects.filter(program__country__in=countries)
        self.fields['program'].queryset = Program.objects.filter(country__in=countries)
        self.fields['office_code'].queryset = Office.objects.filter(province__country__in=countries)
        self.fields['province'].queryset = Province.objects.filter(country__in=countries)


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        exclude = ['create_date', 'edit_date']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.add_input(Submit('submit', 'Save'))

        super(BeneficiaryForm, self).__init__(*args, **kwargs)

        countries = getCountry(self.request.user)
        self.fields['training'].queryset = TrainingAttendance.objects.filter(program__country__in=countries)
        self.fields['training'].queryset = TrainingAttendance.objects.filter(program__country__in=countries)
        self.fields['distribution'].queryset = Distribution.objects.filter(program__country__in=countries)
        self.fields['site'].queryset = SiteProfile.objects.filter(country__in=countries)

