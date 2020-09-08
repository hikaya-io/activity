from import_export import resources
from .models import (
    # TrainingAttendance,
    Distribution,
    Individual,
)

class DistributionResource(resources.ModelResource):

    class Meta:
        model = Distribution


class IndividualResource(resources.ModelResource):

    class Meta:
        model = Individual
