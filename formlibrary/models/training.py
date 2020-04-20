from django.db import models
from .service import Service
from workflow.models import Program, Office, Stakeholder, Contact, Site

class Training(Service):
    trainers = models.ForeignKey(
        Contact, null=True, blank=True, on_delete=models.SET_NULL)
    training_duration = models.IntegerField(help_text="Number of days? Sessions?")

    @property
    def total_individual_supported(self):
        # return len(self.cases)
        return 15

    # @property
    # def attendance(self):
    #     """
    #     ? Return list of Individuals and their attendance as a percentage relative to `training_duration`.
    #     TODO This is related to cases, which keeps track of attendance
    #     """
    #     return {}
