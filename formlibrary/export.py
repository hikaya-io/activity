from import_export import resources  # https://django-import-export.readthedocs.io/en/latest/
from .models import (
    Distribution,
    Individual,
)


class DistributionResource(resources.ModelResource):
    class Meta:
        model = Distribution


class IndividualResource(resources.ModelResource):
    class Meta:
        model = Individual
