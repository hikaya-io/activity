import uuid
from django.db import models
from workflow.models import Program, SiteProfile
from utils.models import CreatedModifiedDates, CreatedModifiedBy
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import os
from uuid import uuid4

phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Invalid Phone Number. Format: '+123456789'. Up to 15 digits allowed.")
email_regex = RegexValidator(
        regex=r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$', message="Invalid Email Address.")


class Case(models.Model):
    """
    Keeps track of Individuals/Households and their usage/participation in services
    Spec: https://github.com/hikaya-io/activity/issues/410
    """
    # ! If Individuals already exist in the database, we change its ID
    # ! to UUID type, and hence can inherit from Case
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    label = models.CharField(max_length=255)


class Household(Case, CreatedModifiedDates, CreatedModifiedBy):
    """
    Family, or group of people, living together
    Spec: https://github.com/hikaya-io/activity/issues/409
    """
    name = models.CharField(max_length=255)
    individuals = models.ForeignKey(
        'Individual', null=True, blank=True, on_delete=models.SET_NULL)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    primary_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    secondary_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.CharField(validators=[email_regex], max_length=100, blank=True)

    def __str__(self):
        if self.name is None:
            return "NULL"
        return self.name


IMAGE_SPEC = {
    "width": 2000,
    "height": 500,
    "limit_kb": 100
}


def validate_image(image, width=IMAGE_SPEC['width'],
                   height=IMAGE_SPEC['height'],
                   limit_kb=IMAGE_SPEC['limit_kb']):
    file_size = image.file.size
    if file_size > limit_kb * 1024:
        raise ValidationError("Max size of file is %s KB" % limit_kb)
    w, h = get_image_dimensions(image)
    if w < width:
        raise ValidationError("Min width is %s" % width)
    if h < height:
        raise ValidationError("Min height is %s" % height)


def path_and_rename(instance, filename):
    upload_to = 'media/images/'
    ext = filename.split('.')[-1]
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join(upload_to, filename)


class Individual(Case, CreatedModifiedDates, CreatedModifiedBy):
    """
    Individual, or person.
    Subject to future changes: https://github.com/hikaya-io/activity/issues/403
    Also, will inherit from Case (subject to research/discussion)
    """
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    sex = models.CharField(choices=SEX_CHOICES, max_length=1, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    household_id = models.ForeignKey(
        Household, null=True, blank=True, on_delete=models.SET_NULL)
    head_of_household = models.BooleanField(default=True)
    id_type = models.CharField(max_length=255, null=True, blank=True)
    id_number = models.CharField(max_length=255, null=True, blank=True)
    primary_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    secondary_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    signature = models.BooleanField(default=True)
    site = models.ForeignKey(
        SiteProfile, null=True, blank=True, on_delete=models.SET_NULL)
    photo = models.FileField(upload_to=path_and_rename, validators=[validate_image], blank=True, null=True)
    description = models.TextField(max_length=550, null=True, blank=True)
    program = models.ForeignKey(
        Program, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def age(self):
        today = date.today()
        delta = relativedelta(today, self.date_of_birth)
        return delta.years

    class Meta:
        ordering = ('first_name',)

    def __str__(self):
        if self.first_name is None:
            return "NULL"
        return self.first_name
