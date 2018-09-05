__all__ = ['telephone_bill']

from dateutil.relativedelta import relativedelta

from django.db import connection
from django.utils import timezone

from sparrow.call_records.exceptions import CurrentMonthForbiddenError, InvalidReferencePeriodError


def telephone_bill(subscriber, *, reference_period=None):
    """
    Returns a bill for the given reference period. If none
    was given, returns a bill for the previous month.

    Prices will be given in Brazilian Real (R$)

    Example of return (pseudo-JSON):
    {
        'subscriber': subscriber,
        'reference_period': 'YYYYMM',
        'call_records': [
            {'destination': '{destination}', 'start_date': '{start_date}', 'start_time': '{start_time}',
             'duration': '0h35m42s', 'price': 'R$ 3,96'},
            # ...
        ]
    }
    """
    if _reference_period_is_current_month(reference_period):
        raise CurrentMonthForbiddenError(reference_period)

    reference_period, start_reference_date, end_reference_date = _calculate_reference_period_bounds(reference_period)
    # NOTE: This has to exist to cover both the following cases:
    # - calls started and ended in the reference period
    # - calls started in the previous month and ended in the reference period
    start_previous_date = start_reference_date - relativedelta(months=1)

    call_records = []
    with connection.cursor() as cursor:
        cursor.execute(_TELEPHONE_BILL_QUERY, {
            'subscriber': subscriber,
            'start_previous_date': start_previous_date,
            'start_reference_date': start_reference_date,
            'end_reference_date': end_reference_date
        })

        for destination, start_timestamp, end_timestamp in cursor.fetchall():
            start_date, start_time = start_timestamp.isoformat().replace('+00:00', 'Z').split('T')
            call_records.append({
                'destination': destination,
                'start_date': start_date,
                'start_time': start_time,
                'duration': _calculate_duration(start_timestamp, end_timestamp),
                'price': _calculate_price(start_timestamp, end_timestamp),
            })

    return {
        'subscriber': subscriber,
        'reference_period': reference_period,
        'call_records': call_records
    }


_TELEPHONE_BILL_QUERY = """
WITH
    start_records AS (
        SELECT
            call_id,
            destination,
            timestamp
        FROM
            call_records_callrecord
        WHERE
            type = 'start'
            AND source = %(subscriber)s
            AND timestamp >= %(start_previous_date)s
            AND timestamp < %(end_reference_date)s
    )

SELECT
    start_records.destination AS destination,
    start_records.timestamp   AS start,
    end_records.timestamp     AS end
FROM
    call_records_callrecord end_records,
    start_records
WHERE
    end_records.type = 'end'
    AND end_records.timestamp >= %(start_reference_date)s
    AND end_records.timestamp < %(end_reference_date)s
    AND start_records.call_id = end_records.call_id
ORDER BY
    start_records.timestamp ASC
"""


def _reference_period_is_current_month(period):
    if not period:
        # NOTE: if no period is given we'll default to the previous
        # month elsewhere
        return False

    try:
        period = timezone.datetime.strptime(period, '%Y%m')
    except (ValueError, TypeError):
        # NOTE: ValueError is for `period` of the right type (string),
        # and TypeError is for other types
        raise InvalidReferencePeriodError(period)

    today = timezone.datetime.today()
    return today.year == period.year and today.month == period.month


def _calculate_reference_period_bounds(period):
    """
    Returns a pair of datetime objects delimiting the reference period given
    as a string in the format of YYYYMM.
    """
    if not period:
        # NOTE: if period is None, consider last month as the period
        period = timezone.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period = (period - relativedelta(months=1)).strftime('%Y%m')

    start_month = timezone.make_aware(timezone.datetime.strptime(period, '%Y%m'))
    end_month = start_month + relativedelta(months=1)

    return (period, start_month, end_month)


def _calculate_duration(start_timestamp, end_timestamp):
    """
    Returns duration in a pretty format, like "32m27s"
    """
    # NOTE: had knowledge of https://gist.github.com/thatalextaylor/7408395
    # so I reused most of it
    seconds = (end_timestamp - start_timestamp).seconds
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    duration = []
    if days > 0:
        duration.append(f'{days}d')
    if hours > 0:
        duration.append(f'{hours}h')
    if minutes > 0:
        duration.append(f'{minutes}m')
    if seconds > 0:
        duration.append(f'{seconds}s')

    return ''.join(duration)


# NOTE: it is stated that price rules can change
# from time to time. In this case, it would be better
# to have multiple functions, one for each price
# rule, and have _calculate_price select the right
# function based on the selected period. This way,
# price calculation will not fluctuate and we'll
# be able to change price rules whenever needed.
#
# Since in this exercise there was no example
# of that, for the purposes of a POC I've decided
# to keep this function simple
def _calculate_price(start_timestamp, end_timestamp):
    """
    Calculates price for the given interval. Values are calculated
    in cents and then converted to Brazilian Real by the end.
    """
    standing_charge = 36
    call_charge = 9
    if start_timestamp.hour >= 22 or start_timestamp.hour < 6:
        # reduced tariff, YAY!
        call_charge = 0

    minutes = (end_timestamp - start_timestamp).seconds // 60
    price = standing_charge + (call_charge * minutes)
    return 'R$ {:0,.2f}'.format(price / 100).replace('.', ',')
