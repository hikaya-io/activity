from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.template import loader

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Submit, Reset, Fieldset, Column, Row
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode

from workflow.models import ActivityUser, ActivityBookmarks, Organization
from .util import send_single_mail


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
        self.fields['organization'].queryset = activity_user.organizations.all()
        # self.fields['user'].error = None
        self.errors['user'] = None
        self.fields['user'].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = ActivityUser
        fields = '__all__'

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.form_tag = False
    helper.layout = Layout(
        # Row(
        #     Column('title', css_class='form-group col-md-6 mb-0'),
        #     Column('employee_number', css_class='form-group col-md-6 mb-0'),
        #     css_class='form-row'
        # ),
        Row(
            Column('user', css_class='form-group col-md-6 mb-0'),
            Column('organization', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('organizations', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        ),
        # 'privacy_disclaimer_accepted',
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
        self.fields['first_name'].label = 'First Name*'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email*'

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = False
    helper.html5_required = True
    helper.form_tag = False
    helper.layout = Layout(
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


class HTMLPasswordResetForm(forms.Form):
    """
    Override Reset Password Form
    """
    email = forms.EmailField(label="Email", max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        active_users = User._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue

            domain = request.build_absolute_uri('/').strip('/')
            context_data = {
                'email': user.email,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, context_data)
            subject = ''.join(subject.splitlines())

            email_txt = 'registration/password_reset_email.txt'
            email_html = 'registration/password_reset_email.html'

            send_single_mail(
                subject,
                'team.hikaya@gmail.com',
                [user.email],
                context_data,
                email_txt,
                email_html
            )
