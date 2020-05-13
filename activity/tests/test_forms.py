from django.test import TestCase
from activity.forms import OrganizationEditForm
from workflow.models import Organization


class FormsTestCase(TestCase):

    def setUp(self):
        self.org_form_data = {
            "name": "Test Organization Name",
            "description": "Test organization description"
        }
        self.form = OrganizationEditForm(data=self.org_form_data)

    def test_form_is_valid(self):
        """Test form is valid """
        self.assertTrue(self.form.is_valid())
        self.assertTrue(self.form.use_required_attribute)
        self.assertEqual(self.form.errors, {})
        self.assertEqual(self.form.data, self.org_form_data)

    def test_helper_info(self):
        """
        Test form helper details
        """
        self.assertEqual(self.form.helper.form_method, 'post')
        self.assertEqual(self.form.helper.form_class, 'form-horizontal')
        self.assertEqual(self.form.helper.label_class, 'col-sm-2')
        self.assertEqual(self.form.helper.field_class, 'col-sm-6')
        self.assertEqual(self.form.helper.form_error_title, 'Form Errors')
        self.assertFalse(self.form.helper.error_text_inline)
        self.assertTrue(self.form.helper.help_text_inline)
        self.assertTrue(self.form.helper.html5_required)
        self.assertEqual(self.form.helper.layout.get_field_names(), [[[0, 0], 'logo']])
