from django.db import models
from .case import Individual
from .training import Training


class Session():
    """
    """
    date = models.DateTimeField()
    training_type = models.ForeignKey(
        Training, null=True, blank=False, on_delete=models.SET_NULL)
    attendees = models.ManyToManyField(Individual, through='Attendance')


class Attendance():
    """
    """
    attendee = models.ForeignKey(Individual, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    attendance = models.BooleanField(default=False)
