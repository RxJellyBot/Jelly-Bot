"""Utilities related to URL strings."""
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

__all__ = ("is_valid_url",)


def is_valid_url(url: str) -> bool:
    """
    Check if ``url`` is a valid URL.

    This calls the Django validator to validate the URL.

    :param url: url to be validated
    :return: if the URL is valid
    """
    try:
        URLValidator()(url)
    except ValidationError:
        return False

    return True
