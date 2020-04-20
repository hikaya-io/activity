from django.db import models
from .service import Service

class Construction(Service):
    # implementer = stakeholder
    status = models.CharField(max_length=255)
