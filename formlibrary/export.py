from import_export import resources
from .models import TrainingAttendance, Distribution, Beneficiary


class TrainingAttendanceResource(resources.ModelResource):

    class Meta:
        model = TrainingAttendance


class DistributionResource(resources.ModelResource):

    class Meta:
        model = Distribution


class BeneficiaryResource(resources.ModelResource):

    class Meta:
        model = Beneficiary