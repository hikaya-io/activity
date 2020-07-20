from django.db import models
from .service import Service
from utils.models import CreatedModifiedBy, CreatedModifiedDates


class Inventory(Service, CreatedModifiedBy, CreatedModifiedDates):
    serviceid = models.ForeignKey(Service, null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=50, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=550, null=False, blank=True)
    quantity = models.IntegerField(null=False, default=0)
    unit = models.CharField(max_length=10, null=False, blank=True)
    unit_cost = models.DecimalField(null=True, blank=True)

    @property
    def total(self):
        return self.quantity * self.unit_cost
