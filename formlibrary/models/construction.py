from django.db import models
from .service import Service


class Construction(Service):
    """
    Service of a construction project
    """
    # implementer = stakeholder
    status = models.CharField(max_length=255)
