__all__ = ['CallRecord']

from django.core.validators import RegexValidator
from django.db import models


phone_number_validator = RegexValidator(
    regex=r'^\d{10,11}$',
    message=('Invalid phone number, format should be AAXXXXXXXXX where AA is '
             'the area code and XXXXXXXXX is the phone number, composed of 8 '
             'to 9 digits')
)


class CallRecord(models.Model):
    """
    Represents a call record, either start or end.
    """
    START = 'st'
    END = 'ed'
    RECORD_TYPES = [
        (START, 'Start'),
        (END, 'End'),
    ]

    type = models.CharField(max_length=2, choices=RECORD_TYPES)
    call_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    source = models.CharField(max_length=11, validators=[phone_number_validator], blank=True)
    destination = models.CharField(max_length=11, validators=[phone_number_validator], blank=True)

    class Meta:
        unique_together = ['type', 'call_id']
