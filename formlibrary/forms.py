from functools import partial
from crispy_forms.helper import FormHelper
from django import forms
from .models import (
    Distribution,
    Individual,
    Household,
    Training,
)
from workflow.models import (
    Office,
    Program,
    SiteProfile,
)


class DatePicker(forms.DateInput):
    """
    Use in form to create a Jquery datepicker element
    """
    template_name = 'datepicker.html'

    DateInput = partial(forms.DateInput, {'class': 'datepicker'})


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

        self.fields['program'].queryset = Program.objects.filter(
            organization=self.request.user.activity_user.organization)
        self.fields['office'].queryset = Office.objects.filter(
            organization=self.request.user.activity_user.organization)

        self.fields['name'].label = '{} name'.format(self.organization.distribution_label)
        self.fields['implementer'].label = '{} implementer'.format(self.organization.distribution_label)


class IndividualForm(forms.ModelForm):

    class Meta:
        model = Individual
        # fields = '__all__'
        exclude = ('created_by', 'modified_by', 'label')

    date_of_birth = forms.DateTimeField(widget=DatePicker.DateInput(), required=False)
    age = forms.CharField(
        label='Age',
        widget=forms.TextInput(attrs={'disabled': True, }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.organization = kwargs.pop('organization')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = True

        super(IndividualForm, self).__init__(*args, **kwargs)

        organization = self.request.user.activity_user.organization
        self.fields['program'].queryset = Program.objects.filter(
            organization=organization)
        self.fields['site'].queryset = SiteProfile.objects.filter(
            organizations__id__contains=self.request.user.activity_user.organization.id)
        self.fields['household_id'].queryset = Household.objects.filter(organization=organization)
        self.fields['age'].initial = str(self.instance.age)


class HouseholdForm(forms.ModelForm):

    class Meta:
        model = Household
        fields = '__all__'
        exclude = ['create_date', 'edit_date', 'created_by', 'label', 'organization', 'modified_by']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.organization = kwargs.pop('organization')
        self.request = kwargs.pop('request')
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True

        super(HouseholdForm, self).__init__(*args, **kwargs)
        organization = self.request.user.activity_user.organization
        self.fields['program'].queryset = Program.objects.filter(
            organization=organization)
        self.fields['name'].label = '{} name'.format(self.organization.household_label)


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['create_date', 'edit_date', 'created_by', 'label', 'organization', 'modified_by']

    start_date = forms.DateTimeField(widget=DatePicker.DateInput(), required=True)
    end_date = forms.DateTimeField(widget=DatePicker.DateInput(), required=True)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.organization = kwargs.pop('organization')
        self.request = kwargs.pop('request')
        self.helper.form_method = 'post'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True

        super(TrainingForm, self).__init__(*args, **kwargs)

        self.fields['program'].queryset = Program.objects.filter(
            organization=self.request.user.activity_user.organization)
        self.fields['office'].queryset = Office.objects.filter(
            organization=self.request.user.activity_user.organization)

        self.fields['name'].label = '{} name'.format(self.organization.training_label)
        self.fields['implementer'].label = '{} implementer'.format(self.organization.training_label)
