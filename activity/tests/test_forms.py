from django.test import TestCase
from activity.forms import OrganizationEditForm
from workflow.models import Organization


class FormsTestCase(TestCase):

    def test_form_is_valid(self):
        """Test form is valid """
        org_form_data = {
            "name": "Test Organization Name",
            "description": "Test organization description"
        }
        form = OrganizationEditForm(data=org_form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.use_required_attribute)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.data, org_form_data)

    def test_helper_info(self):
        """
        Test form helper details
        """
        org_form_data = {
            "name": "Test Organization Name",
            "description": "Test organization description"
        }
        form = OrganizationEditForm(data=org_form_data)
        self.assertEqual(form.helper.form_method, 'post')
        self.assertEqual(form.helper.form_class, 'form-horizontal')
        self.assertEqual(form.helper.label_class, 'col-sm-2')
        self.assertEqual(form.helper.field_class, 'col-sm-6')
        self.assertEqual(form.helper.form_error_title, 'Form Errors')
        self.assertFalse(form.helper.error_text_inline)
        self.assertTrue(form.helper.help_text_inline)
        self.assertTrue(form.helper.html5_required)
        self.assertEqual(form.helper.layout.get_field_names(), [[[0, 0], 'logo']])