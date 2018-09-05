import pytest
from freezegun import freeze_time

from sparrow.call_records.api import telephone_bill
from sparrow.call_records.exceptions import CurrentMonthForbiddenError, InvalidReferencePeriodError
from sparrow.call_records.models import CallRecord
from .utils import tzdatetime


@pytest.mark.django_db
def test_telephone_bill_within_reference_period():
    subscriber = '1132547698'

    CallRecord.objects.bulk_create([
        # A few incomplete pairs that _should_ be ignored
        CallRecord(type=CallRecord.START, call_id=0, timestamp=tzdatetime(2018, 1, 1, 3, 0),
                   source=subscriber, destination='21987654321'),
        CallRecord(type=CallRecord.END, call_id=20, timestamp=tzdatetime(2018, 1, 17, 3, 5)),

        # A few _complete_ pairs that _should_ be on the bill
        CallRecord(type=CallRecord.START, call_id=1, timestamp=tzdatetime(2018, 1, 1, 10, 0),
                   source=subscriber, destination='21987654321'),
        CallRecord(type=CallRecord.END, call_id=1, timestamp=tzdatetime(2018, 1, 1, 10, 2)),

        CallRecord(type=CallRecord.START, call_id=2, timestamp=tzdatetime(2018, 1, 2, 7, 35),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=2, timestamp=tzdatetime(2018, 1, 2, 8, 2)),

        CallRecord(type=CallRecord.START, call_id=3, timestamp=tzdatetime(2018, 1, 5, 23, 2),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=3, timestamp=tzdatetime(2018, 1, 5, 23, 57)),

        # A few call records that belong to another source
        # that also _should_ be ignored
        CallRecord(type=CallRecord.START, call_id=17, timestamp=tzdatetime(2018, 1, 5, 23, 2),
                   source='2798765432', destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=17, timestamp=tzdatetime(2018, 1, 5, 23, 57)),
        CallRecord(type=CallRecord.START, call_id=18, timestamp=tzdatetime(2018, 1, 6, 17, 27),
                   source='2798765432', destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=29, timestamp=tzdatetime(2018, 1, 21, 20, 20)),
    ])

    bill = telephone_bill(subscriber, reference_period='201801')

    assert bill == {
        'subscriber': subscriber,
        'reference_period': '201801',
        'call_records': [
            {'destination': '21987654321', 'start_date': '2018-01-01', 'start_time': '10:00:00Z',
             'duration': '2m', 'price': 'R$ 0,54'},
            {'destination': '2133445566', 'start_date': '2018-01-02', 'start_time': '07:35:00Z',
             'duration': '27m', 'price': 'R$ 2,79'},

            # This one is on reduced tariff
            {'destination': '2133445566', 'start_date': '2018-01-05', 'start_time': '23:02:00Z',
             'duration': '55m', 'price': 'R$ 0,36'},
        ]
    }


@pytest.mark.django_db
def test_telephone_bill_call_finished_next_month_must_be_excluded():
    # For a given reference period, any calls that have ENDED
    # in the next month MUST NOT be added
    subscriber = '1132547698'

    CallRecord.objects.bulk_create([
        # A few _complete_ pairs that _should_ be on the bill
        CallRecord(type=CallRecord.START, call_id=1, timestamp=tzdatetime(2018, 1, 30, 23, 2),
                   source=subscriber, destination='21987654321'),
        CallRecord(type=CallRecord.END, call_id=1, timestamp=tzdatetime(2018, 2, 1, 2, 24)),
    ])

    bill = telephone_bill(subscriber, reference_period='201801')

    assert bill == {
        'subscriber': subscriber,
        'reference_period': '201801',
        'call_records': []
    }


@pytest.mark.django_db
def test_telephone_bill_call_finished_beginning_month_must_be_added():
    # For a given reference period, any calls that have STARTED
    # on the past month and ENDED in the current month
    # MUST be added
    subscriber = '1132547698'

    CallRecord.objects.bulk_create([
        # A few _complete_ pairs that _should_ be on the bill
        CallRecord(type=CallRecord.START, call_id=1, timestamp=tzdatetime(2018, 1, 30, 23, 2),
                   source=subscriber, destination='21987654321'),
        CallRecord(type=CallRecord.END, call_id=1, timestamp=tzdatetime(2018, 2, 1, 2, 24)),
    ])

    bill = telephone_bill(subscriber, reference_period='201802')

    assert bill == {
        'subscriber': subscriber,
        'reference_period': '201802',
        'call_records': [
            {'destination': '21987654321', 'start_date': '2018-01-30', 'start_time': '23:02:00Z',
             'duration': '3h22m', 'price': 'R$ 0,36'},
        ]
    }


@pytest.mark.django_db
def test_telephone_bill_standard_tariff():
    subscriber = '1132547698'

    CallRecord.objects.bulk_create([
        CallRecord(type=CallRecord.START, call_id=1, timestamp=tzdatetime(2018, 1, 1, 10, 0),
                   source=subscriber, destination='21987654321'),
        CallRecord(type=CallRecord.END, call_id=1, timestamp=tzdatetime(2018, 1, 1, 10, 2)),
    ])

    bill = telephone_bill(subscriber, reference_period='201801')

    assert bill == {
        'subscriber': subscriber,
        'reference_period': '201801',
        'call_records': [
            {'destination': '21987654321', 'start_date': '2018-01-01', 'start_time': '10:00:00Z',
             'duration': '2m', 'price': 'R$ 0,54'},
        ]
    }


@pytest.mark.django_db
def test_telephone_bill_reduced_tariff():
    subscriber = '1132547698'

    CallRecord.objects.bulk_create([
        CallRecord(type=CallRecord.START, call_id=3, timestamp=tzdatetime(2018, 1, 5, 23, 2),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=3, timestamp=tzdatetime(2018, 1, 5, 23, 57)),
    ])

    bill = telephone_bill(subscriber, reference_period='201801')

    assert bill == {
        'subscriber': subscriber,
        'reference_period': '201801',
        'call_records': [
            {'destination': '2133445566', 'start_date': '2018-01-05', 'start_time': '23:02:00Z',
             'duration': '55m', 'price': 'R$ 0,36'},
        ]
    }


@freeze_time('2018-01-21')
def test_get_telephone_bill_current_month_should_fail():
    with pytest.raises(CurrentMonthForbiddenError):
        telephone_bill('1212345678', reference_period='201801')


@freeze_time('2018-03-17')
@pytest.mark.django_db
def test_get_telephone_bill_no_reference_period_uses_last_month():
    subscriber = '1132547698'

    CallRecord.objects.bulk_create([
        # Since these are too old (bill is supposed to infer 201802),
        # they SHOULD NOT be added to the bill
        CallRecord(type=CallRecord.START, call_id=11, timestamp=tzdatetime(2018, 1, 1, 10, 0),
                   source=subscriber, destination='21987654321'),
        CallRecord(type=CallRecord.END, call_id=11, timestamp=tzdatetime(2018, 1, 1, 10, 2)),
        CallRecord(type=CallRecord.START, call_id=12, timestamp=tzdatetime(2018, 1, 2, 7, 35),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=12, timestamp=tzdatetime(2018, 1, 2, 8, 2)),

        # These are pairs from the previous month
        CallRecord(type=CallRecord.START, call_id=1, timestamp=tzdatetime(2018, 2, 1, 10, 0),
                   source=subscriber, destination='21987654321'),
        CallRecord(type=CallRecord.END, call_id=1, timestamp=tzdatetime(2018, 2, 1, 10, 2)),

        CallRecord(type=CallRecord.START, call_id=2, timestamp=tzdatetime(2018, 2, 2, 7, 35),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=2, timestamp=tzdatetime(2018, 2, 2, 8, 2)),

        CallRecord(type=CallRecord.START, call_id=3, timestamp=tzdatetime(2018, 2, 5, 23, 2),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=3, timestamp=tzdatetime(2018, 2, 5, 23, 57)),

        # These belong to the current month and SHOULD NOT be added as well
        CallRecord(type=CallRecord.START, call_id=22, timestamp=tzdatetime(2018, 3, 2, 7, 35),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=22, timestamp=tzdatetime(2018, 3, 2, 8, 2)),

        CallRecord(type=CallRecord.START, call_id=23, timestamp=tzdatetime(2018, 3, 5, 23, 2),
                   source=subscriber, destination='2133445566'),
        CallRecord(type=CallRecord.END, call_id=23, timestamp=tzdatetime(2018, 3, 5, 23, 57)),
    ])

    bill = telephone_bill(subscriber, reference_period=None)

    assert bill == {
        'subscriber': subscriber,
        'reference_period': '201802',
        'call_records': [
            {'destination': '21987654321', 'start_date': '2018-02-01', 'start_time': '10:00:00Z',
             'duration': '2m', 'price': 'R$ 0,54'},
            {'destination': '2133445566', 'start_date': '2018-02-02', 'start_time': '07:35:00Z',
             'duration': '27m', 'price': 'R$ 2,79'},

            # This one is on reduced tariff
            {'destination': '2133445566', 'start_date': '2018-02-05', 'start_time': '23:02:00Z',
             'duration': '55m', 'price': 'R$ 0,36'},
        ]
    }


def test_get_telephone_bill_invalid_reference_period_should_fail():
    with pytest.raises(InvalidReferencePeriodError):
        telephone_bill('1212345678', reference_period='a')
    with pytest.raises(InvalidReferencePeriodError):
        telephone_bill('1212345678', reference_period=True)
    with pytest.raises(InvalidReferencePeriodError):
        telephone_bill('1212345678', reference_period=42)
