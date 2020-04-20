from django.db import models
from .service import Service

class Training(Service):
    # implementer = stakeholder
    training_duration = models.IntegerField()
    # trainers = 

    @property
    def total_individual_supported(self):
        return 999

    @property
    def attendance(self):
        """
        ? Return list of Individuals and their attendance as a percentage relative to `training_duration`.
        TODO This is related to cases, which keeps track of attendance
        """
        return {}
