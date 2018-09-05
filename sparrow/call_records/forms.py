__all__ = ['TelephoneBillForm']

from django import forms
from django.core.validators import RegexValidator

from sparrow.call_records.models import phone_number_validator


class TelephoneBillForm(forms.Form):
    subscriber = forms.CharField(max_length=11, validators=[
        phone_number_validator
    ])
    reference_period = forms.CharField(max_length=6, validators=[
        RegexValidator(
            regex=r'^\d{6}$',
            message='Reference period should be in the YYYYMM format'
        )
    ], required=False)
