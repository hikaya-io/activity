import uuid
from django.db import models
from workflow.models import Program, Office, Stakeholder, Site
from formlibrary.models import Case

# https://github.com/hikaya-io/activity/issues/412
class Service(models.Model):
    """
    Abstract base class for all kinds of offered services
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=550, null=True, blank=True)
    program = models.OneToOneField(
        Program, null=True, blank=True, on_delete=models.SET_NULL)
    office = models.OneToOneField(
        Office, null=True, blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey(
        Site, null=True, blank=True, on_delete=models.SET_NULL)
    implementer = models.OneToOneField(
        Stakeholder, null=True, blank=True, on_delete=models.SET_NULL)
    cases = models.ForeignKey(
        Case, null=True, blank=True, on_delete=models.SET_NULL)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    form_verified_by = models.CharField(max_length=255)

    class Meta:
        abstract = True