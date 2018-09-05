from django.utils import timezone


def tzdatetime(*args):
    return timezone.make_aware(timezone.datetime(*args))
