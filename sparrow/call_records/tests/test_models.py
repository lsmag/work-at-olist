import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from model_mommy import mommy

from sparrow.call_records.models import CallRecord


@pytest.mark.django_db
def test_start_call_record_uniqueness():
    start_record = CallRecord.objects.create(type=CallRecord.START, call_id=42, timestamp=timezone.now())
    with pytest.raises(IntegrityError):
        CallRecord.objects.create(type=CallRecord.START, call_id=42, timestamp=start_record.timestamp)


@pytest.mark.django_db
def test_end_call_record_uniqueness():
    end_record = CallRecord.objects.create(type=CallRecord.END, call_id=42, timestamp=timezone.now())
    with pytest.raises(IntegrityError):
        CallRecord.objects.create(type=CallRecord.END, call_id=42, timestamp=end_record.timestamp)


@pytest.mark.parametrize('field, value', [
    ('source', '9912345678'),
    ('source', '99123456789'),
    ('destination', '9912345678'),
    ('destination', '99123456789'),
])
def test_call_record_phone_number_validation(field, value):
    record = mommy.prepare(CallRecord, **{field: value})
    # NOTE: this _should not_ raise IntegrityError
    record.clean_fields()


@pytest.mark.parametrize('field, value', [
    ('source', 'a'),
    ('source', '~'),
    ('source', '12345'),
    ('source', '1234567'),  # too short
    ('source', '123456789012'),  # too long
    ('destination', 'a'),
    ('destination', '~'),
    ('destination', '12345'),
    ('destination', '1234567'),  # too short
    ('destination', '123456789012'),  # too long
])
def test_call_record_phone_number_invalid_inputs(field, value):
    record = mommy.prepare(CallRecord, **{field: value})

    with pytest.raises(ValidationError):
        record.clean_fields()
