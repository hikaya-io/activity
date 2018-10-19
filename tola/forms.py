from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset, Div
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from workflow.models import TolaUser, TolaBookmarks
from django.contrib.auth.models import User



class RegistrationForm(UserChangeForm):
    """
    Form for registering a new account.
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial')
        super(RegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['password']
        print user['username'].is_superuser
        # if they aren't a super user or User Admin don't let them change countries form field
        if 'User Admin' not in user['username'].groups.values_list('name', flat=True) and not user['username'].is_superuser:
            self.fields['countries'].widget.attrs['disabled'] = "disabled"
            self.fields['country'].widget.attrs['disabled'] = "disabled"

    class Meta:
        model = TolaUser
        fields = '__all__'


    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.layout = Layout(Fieldset('','title', 'name', 'employee_number', 'user', 'username',
                                    'country', 'countries','modified_by','created','updated'),
                           Submit('submit', 'Submit', css_class='btn-default'),
                           Reset('reset', 'Reset', css_class='btn-warning'))


class NewUserRegistrationForm(UserCreationForm):
    """
    Form for registering a new account.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name','email','username']

    def __init__(self, *args, **kwargs):
        super(NewUserRegistrationForm, self).__init__(*args, **kwargs)


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


class NewTolaUserRegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    class Meta:
        model = TolaUser
        fields = ['title', 'country', 'privacy_disclaimer_accepted']

    def __init__(self, *args, **kwargs):
        super(NewTolaUserRegistrationForm, self).__init__(*args, **kwargs)

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
        Fieldset('Information','title', 'country'),
        Fieldset('Privacy Statement','privacy_disclaimer_accepted',),

    )

class BookmarkForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    class Meta:
        model = TolaBookmarks
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
        Fieldset('','name','bookmark_url'),
        Submit('submit', 'Submit', css_class='btn-default'),
        Reset('reset', 'Reset', css_class='btn-warning'))


