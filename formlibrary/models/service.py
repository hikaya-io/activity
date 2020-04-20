import uuid
from django.db import models

# https://github.com/hikaya-io/activity/issues/412
class Service(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=550, null=True, blank=True)
    # program = 
    # office = 
    # site = 
    # implementer = 
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Are these attribute common to all (potential) ServiceTypes?
    form_verified_by = models.CharField(max_length=255)
    # case_label =
    # ? Test score. Related to Cases?

    class Meta:
        abstract = True