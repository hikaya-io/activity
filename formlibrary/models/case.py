import uuid
from django.db import models
from workflow.models import Program, SiteProfile
from utils.models import CreatedModifiedDates, CreatedModifiedBy


class Case(CreatedModifiedDates, CreatedModifiedBy):
    """
    Keeps track of Individuals/Households and their usage/participation in services
    Spec: https://github.com/hikaya-io/activity/issues/410
    """
    # ! If Individuals already exist in the database, we change its ID
    # ! to UUID type, and hence can inherit from Case
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    label = models.CharField(max_length=255)
    # the many to many relationship is defined in Service, so django 
    # should add a field with the Services automatically (I may be wrong on this though)


class Household(Case):
    """
    Family, or group of people, living together
    Spec: https://github.com/hikaya-io/activity/issues/409
    """
    name = models.CharField(max_length=255)


class Individual(CreatedModifiedDates):
    """
    Individual, or person.
    Subject to future changes: https://github.com/hikaya-io/activity/issues/403
    Also, will inherit from Case (subject to research/discussion)
    """
    first_name = models.CharField(max_length=255, null=True, blank=True)
    training = models.ManyToManyField("formlibrary.training", blank=True)
    distribution = models.ManyToManyField("formlibrary.distribution", blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    site = models.ForeignKey(SiteProfile, null=True,
                             blank=True, on_delete=models.SET_NULL)
    signature = models.BooleanField(default=True)
    remarks = models.TextField(max_length=550, null=True, blank=True)
    program = models.ManyToManyField(Program, blank=True)

    household = models.ForeignKey(
        Household, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('first_name',)

    def __str__(self):
        return self.first_name
