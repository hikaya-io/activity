#!/usr/bin/python3
# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.layout import Layout, Submit, Reset
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from workflow.models import ActivityUser, ActivityBookmarks, Organization
from django.forms .models import model_to_dict


class RegistrationForm(UserChangeForm):
    """
    Form for registering a new account.
    """

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial')
        super(RegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['password']
        # if they aren't a super user or User Admin
        # don't let them change countries form field
        if 'User Admin' not in user['username'].groups.\
                values_list('name', flat=True) \
                and not user['username'].is_superuser:
            self.fields['organizations'].widget.attrs['disabled'] = 'disabled'
            self.fields['user'].widget.attrs['disabled'] = 'disabled'

        activity_user = ActivityUser.objects.get(user=user['username'])
        print(model_to_dict(activity_user))
        self.fields['organization'].queryset = activity_user.organizations.all()

    class Meta:
        model = ActivityUser
        fields = '__all__'

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.layout = Layout(
        Row(
            Column('title', css_class='form-group col-md-6 mb-0'),
            Column('employee_number', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('user', css_class='form-group col-md-6 mb-0'),
            Column('organization', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('organizations', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        ),
        'privacy_disclaimer_accepted',
        
        HTML('<a class="btn btn-warning mr-3" href={% url "index" %}>Close</a>'),
        Submit('submit', 'Save Changes', css_class='btn-md btn-success'),
    )


class NewUserRegistrationForm(UserCreationForm):
    """
    Form for registering a new account.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def __init__(self, *args, **kwargs):
        super(NewUserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = False
    helper.html5_required = True
    helper.form_tag = False
    helper.layout = Layout(
        'name',
        Row(
            Column('first_name', css_class='form-group col-md-6 mb-0'),
            Column('last_name', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('username', css_class='form-group col-md-6 mb-0'),
            Column('email', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
    )


class NewActivityUserRegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """

    class Meta:
        model = ActivityUser
        fields = ['title', 'country', 'privacy_disclaimer_accepted']

    def __init__(self, *args, **kwargs):
        super(NewActivityUserRegistrationForm, self).__init__(*args, **kwargs)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.form_tag = False
    helper.layout = Layout(
        Fieldset('Information', 'title', 'country'),
        Fieldset('Privacy Statement', 'privacy_disclaimer_accepted', ),

    )


class BookmarkForm(forms.ModelForm):
    """
    Form for registering a new account.
    """

    class Meta:
        model = ActivityBookmarks
        fields = ['name', 'bookmark_url']

    def __init__(self, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.form_tag = True
    helper.layout = Layout(
        Fieldset('', 'name', 'bookmark_url'),
        Submit('submit', 'Submit', css_class='btn-success'),
        Reset('reset', 'Reset', css_class='btn-warning'))


class OrganizationEditForm(forms.ModelForm):
    """
    Form for changing logo via User's profile page
    """
    class Meta:
        model = Organization
        fields = ['logo', ]

    def __init__(self, *args, **kwargs):
        super(OrganizationEditForm, self).__init__(*args, **kwargs)
        self.fields['logo'].label = ''
    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.layout = Layout(
        Fieldset('', 'logo',))
