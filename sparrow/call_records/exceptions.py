__all__ = ['CurrentMonthForbiddenError', 'InvalidReferencePeriodError']


class TelephoneBillError(Exception):
    pass


class CurrentMonthForbiddenError(TelephoneBillError):
    """
    Raised when `sparrow.call_records.api.telephone_bill` is called
    with a reference period that is equivalent to the current month.
    """

    def __init__(self, reference_period):
        super().__init__(f'Reference period {reference_period} is not closed yet')


class InvalidReferencePeriodError(TelephoneBillError):
    def __init__(self, invalid_period):
        super().__init__(f'Invalid reference period {invalid_period}, should be string in the format YYYYMM')
