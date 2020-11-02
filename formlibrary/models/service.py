import uuid
from django.db import models
from utils.models import CreatedModifiedBy, CreatedModifiedDates, StartEndDates
from .case import Case
from workflow.models import (
    Contact,
    Office,
    Program,
    SiteProfile,
    Stakeholder,
)

SERVICE_TYPES = {
    "training",
    "distribution"
}


class Service(CreatedModifiedBy, CreatedModifiedDates, StartEndDates):
    """
    Abstract base class for all kinds of offered services (distributions, trainings...)
    Spec: https://github.com/hikaya-io/activity/issues/412
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=550, null=True, blank=True)
    # Is a Program required for any type of service?
    program = models.ForeignKey(
        Program, null=True, blank=False, on_delete=models.SET_NULL)
    office = models.ForeignKey(
        Office, null=True, blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(
        SiteProfile, null=True, blank=True, on_delete=models.SET_NULL)
    implementer = models.ForeignKey(  # Can an implementer be in charge of multiple services?
        Stakeholder, null=True, blank=True, on_delete=models.SET_NULL)
    cases = models.ManyToManyField(Case, blank=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    form_verified_by = models.CharField(max_length=255, null=True, blank=True)
    form_completed_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    @property
    def total_supported(self):
        """
        Number of Individuals, including Households, linked to the service
        """
        return 0

    @property
    def total_individuals_supported(self):
        """
        Number of Individuals, excluding Households, linked to the service
        """
        return 0

    @property
    def total_households_supported(self):
        """
        Number of Households linked to the service
        """
        return 0

    def get_service_types(self):
        return SERVICE_TYPES
