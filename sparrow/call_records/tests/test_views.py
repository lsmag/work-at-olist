import json
import pytest
from freezegun import freeze_time
from operator import itemgetter

from django.urls import reverse
from rest_framework import status

from sparrow.call_records.models import CallRecord, invalid_phone_number_message
from .utils import tzdatetime


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
    error_messages = [invalid_phone_number_message]
    if len(invalid_value) > 11:
        error_messages.append('Ensure this field has no more than 11 characters.')

    assert json.loads(response.content) == {field: error_messages}


@freeze_time('2018-02-04')
@pytest.mark.parametrize('reference_period', ['201801', None])
@pytest.mark.django_db
def test_get_telephone_bill(client, reference_period):
    subscriber = '1198761234'
    CallRecord.objects.bulk_create([
        CallRecord(type=CallRecord.START, call_id=12, timestamp=tzdatetime(2018, 1, 1, 10),
                   source=subscriber, destination='2199997777'),
        CallRecord(type=CallRecord.END, call_id=12, timestamp=tzdatetime(2018, 1, 1, 11)),

        CallRecord(type=CallRecord.START, call_id=21, timestamp=tzdatetime(2018, 1, 2, 11),
                   source=subscriber, destination='2199997777'),
        CallRecord(type=CallRecord.END, call_id=21, timestamp=tzdatetime(2018, 1, 2, 12)),

        CallRecord(type=CallRecord.START, call_id=32, timestamp=tzdatetime(2018, 1, 3, 12),
                   source=subscriber, destination='2199997777'),
        CallRecord(type=CallRecord.END, call_id=32, timestamp=tzdatetime(2018, 1, 3, 14)),
    ])

    response = client.get(reverse('call_records:telephone_bill'), data={
        'subscriber': subscriber,
        'reference_period': '201801'
    })

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == {
        'subscriber': subscriber,
        'reference_period': '201801',
        'call_records': [
            {'destination': '2199997777',
             'duration': '1h',
             'price': 'R$ 5,76',
             'start_date': '2018-01-01',
             'start_time': '10:00:00Z'},
            {'destination': '2199997777',
             'duration': '1h',
             'price': 'R$ 5,76',
             'start_date': '2018-01-02',
             'start_time': '11:00:00Z'},
            {'destination': '2199997777',
             'duration': '2h',
             'price': 'R$ 11,16',
             'start_date': '2018-01-03',
             'start_time': '12:00:00Z'}
        ]
    }


@freeze_time('2018-02-04')
def test_get_telephone_bill_current_month_should_fail(client):
    response = client.get(reverse('call_records:telephone_bill'), data={
        'subscriber': '1122334455',
        'reference_period': '201802'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {'detail': 'Reference period 201802 is not closed yet'}


def test_get_telephone_bill_missing_subscriber(client):
    response = client.get(reverse('call_records:telephone_bill'), data={
        'reference_period': '201801'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {'subscriber': ['This field is required.']}


@pytest.mark.parametrize('subscriber, expected_errors', [
    ('', ['This field is required.']),
    ('a', [invalid_phone_number_message]),
    ('~', [invalid_phone_number_message]),
    ('123456', [invalid_phone_number_message]),  # too short
    ('11234523452345',  [invalid_phone_number_message,  # too long
                         'Ensure this value has at most 11 characters (it has 14).']),
])
def test_get_telephone_bill_invalid_subscriber(client, subscriber, expected_errors):
    response = client.get(reverse('call_records:telephone_bill'), data={
        'subscriber': subscriber,
        'reference_period': '201801'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {'subscriber': expected_errors}


standard_regex_period_error = 'Reference period should be in the YYYYMM format'


@pytest.mark.parametrize('reference_period, expected_errors', [
    ('a', [standard_regex_period_error]),
    ('12345', [standard_regex_period_error]),  # too short
    ('2233445', [standard_regex_period_error, 'Ensure this value has at most 6 characters (it has 7).']),  # too long
    (12, [standard_regex_period_error]),
    (True, [standard_regex_period_error]),
])
@pytest.mark.django_db
def test_get_telephone_bill_invalid_reference_period(client, reference_period, expected_errors):
    response = client.get(reverse('call_records:telephone_bill'), data={
        'subscriber': '1198765432',
        'reference_period': reference_period
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {'reference_period': expected_errors}
