from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

__all__ = ["is_valid_url"]


def is_valid_url(url: str) -> bool:
    try:
        URLValidator()(url)
    except ValidationError:
        return False

    return True
