from django.utils import timezone


def timestamp():
    """Same format as those seen when running the development server."""
    dt = timezone.now()
    return f'[{dt.strftime("%d/%b/%Y %H:%M:%S")}] '