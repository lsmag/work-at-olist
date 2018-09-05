import json
import pytest
from operator import itemgetter

from django.utils import timezone
from django.urls import reverse
from rest_framework import status

from sparrow.call_records.models import CallRecord


def tzdatetime(*args):
    return timezone.make_aware(timezone.datetime(*args))


def record_to_json(record):
    record_data = {
        'id': record.id,
        'type': record.type,
        'call_id': record.call_id,
        # NOTE: the replace below is to conform with DRF's serializer format
        'timestamp': record.timestamp.isoformat().replace('+00:00', 'Z'),
    }

    if record.is_start_record:
        record_data.update({
            'source': record.source,
            'destination': record.destination
        })

    return record_data


def records_to_json(records):
    return [record_to_json(record)
            for record in records]


@pytest.mark.django_db
def test_get_call_records(client):
    records = CallRecord.objects.bulk_create([
        CallRecord(type=CallRecord.START, call_id=12, timestamp=tzdatetime(2018, 1, 1),
                   source='2199998888', destination='2199997777'),
        CallRecord(type=CallRecord.START, call_id=21, timestamp=tzdatetime(2018, 1, 2),
                   source='2199998888', destination='2199997777'),
        CallRecord(type=CallRecord.START, call_id=32, timestamp=tzdatetime(2018, 1, 3),
                   source='2199998888', destination='2199997777'),

        CallRecord(type=CallRecord.END, call_id=21, timestamp=tzdatetime(2018, 1, 4)),
        CallRecord(type=CallRecord.END, call_id=32, timestamp=tzdatetime(2018, 1, 5)),
    ])

    response = client.get(reverse('call_records:index'))

    assert (sorted(json.loads(response.content), key=itemgetter('timestamp'))
            == sorted(records_to_json(records), key=itemgetter('timestamp')))


@pytest.mark.django_db
def test_post_start_call_record(client):
    response = client.post(reverse('call_records:index'), data={
        'type': CallRecord.START,
        'call_id': 21,
        'timestamp': tzdatetime(2018, 5, 17),
        'source': '2199887766',
        'destination': '21887766551'
    })

    assert response.status_code == status.HTTP_201_CREATED
    created_record = CallRecord.objects.get(type=CallRecord.START, call_id=21)
    assert json.loads(response.content) == record_to_json(created_record)


@pytest.mark.django_db
def test_post_end_call_record(client):
    response = client.post(reverse('call_records:index'), data={
        'type': CallRecord.END,
        'call_id': 21,
        'timestamp': tzdatetime(2018, 5, 17),
    })

    assert response.status_code == status.HTTP_201_CREATED
    created_record = CallRecord.objects.get(type=CallRecord.END, call_id=21)
    assert json.loads(response.content) == record_to_json(created_record)


def test_post_invalid_type(client):
    response = client.post(reverse('call_records:index'), data={
        'type': 'whatever',
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {'type': ['Only "start" or "end" are allowed']}


@pytest.mark.parametrize('record_type', [CallRecord.START, CallRecord.END])
@pytest.mark.django_db
def test_post_duplicated_call_id(client, record_type):
    CallRecord.objects.create(type=record_type, call_id=11, timestamp=tzdatetime(2011, 2, 3))
    response = client.post(reverse('call_records:index'), data={
        'type': record_type,
        'call_id': 11,
        'timestamp': tzdatetime(2012, 3, 4),
        'source': '1198769876',
        'destination': '1198769876',
    })

    assert response.status_code == status.HTTP_409_CONFLICT
    assert json.loads(response.content) == {'detail': 'Call record already exists'}


@pytest.mark.parametrize('record_type', [CallRecord.START, CallRecord.END])
def test_post_data_missing_timestamp(client, record_type):
    response = client.post(reverse('call_records:index'), data={
        'type': record_type,
        'call_id': 11,
        'source': '1198769876',
        'destination': '1198769876',
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {'timestamp': ['This field is required.']}


@pytest.mark.parametrize('missing_field', ['source', 'destination'])
def test_post_start_record_missing_phone_number(client, missing_field):
    data = {
        'type': CallRecord.START,
        'call_id': 11,
        'timestamp': tzdatetime(2012, 3, 4),
        'source': '1198769876',
        'destination': '1198769876',
    }

    del data[missing_field]
    response = client.post(reverse('call_records:index'), data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {missing_field: ['This field is required.']}


@pytest.mark.parametrize('field', ['source', 'destination'])
def test_post_start_record_blank_phone_number(client, field):
    data = {
        'type': CallRecord.START,
        'call_id': 11,
        'timestamp': tzdatetime(2012, 3, 4),
        # These are valid values
        'source': '1198769876',
        'destination': '1198769876',
    }

    # now we're overriding with an empty string for the sake of the test
    data[field] = ''

    response = client.post(reverse('call_records:index'), data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {field: ['This field may not be blank.']}

@pytest.mark.parametrize('field, invalid_value', [
    ('source', 'a'),
    ('source', '~'),
    ('source', '23'),
    ('source', '0012345678123'),
    ('destination', 'a'),
    ('destination', '~'),
    ('destination', '23'),
    ('destination', '0012345678123'),
])
def test_post_start_record_invalid_phone_number(client, field, invalid_value):
    data = {
        'type': CallRecord.START,
        'call_id': 11,
        'timestamp': tzdatetime(2012, 3, 4),
        # These are valid values
        'source': '1198769876',
        'destination': '1198769876',
    }

    # now we're overriding with the parametrized _invalid_ value for the sake of the test
    data[field] = invalid_value

    response = client.post(reverse('call_records:index'), data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error_messages = [('Invalid phone number, format should be AAXXXXXXXXX where AA '
                       'is the area code and XXXXXXXXX is the phone number, composed '
                       'of 8 to 9 digits')]
    if len(invalid_value) > 11:
        error_messages.append('Ensure this field has no more than 11 characters.')

    assert json.loads(response.content) == {field: error_messages}
