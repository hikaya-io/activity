import uuid
from django.db import models
from datetime import datetime
from workflow.models import Program, SiteProfile
from .training_attendance import TrainingAttendance
from .distribution import Distribution

# https://github.com/hikaya-io/activity/issues/410
class Case(models.Model):
    """
    Keeps track of Individuals/Households and their usage/participation in services
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
    # services = 

# class Individual(Case):
class Individual(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    training = models.ManyToManyField(TrainingAttendance, blank=True)
    distribution = models.ManyToManyField(Distribution, blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    site = models.ForeignKey(SiteProfile, null=True,
                             blank=True, on_delete=models.SET_NULL)
    signature = models.BooleanField(default=True)
    remarks = models.TextField(max_length=550, null=True, blank=True)
    program = models.ManyToManyField(Program, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('first_name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Individual, self).save()

    # displayed in admin templates
    def __str__(self):
        if self.first_name is None:
            return "NULL"
        return self.first_name

# https://github.com/hikaya-io/activity/issues/409
class Household(Case):
    name = models.CharField(max_length=255)
    # individuals = 
    # ? address
    # ? contact_information

# class Village(Case):
#    individuals = 

# class School(Case):
#     students = individuals