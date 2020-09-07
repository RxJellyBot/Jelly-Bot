"""Relay for CSRF exemption."""
from abc import ABC

from django.views import View
from django.views.decorators.csrf import csrf_exempt


class CsrfExemptRelay(View, ABC):
    """Relay for CSRF exemption. This will be needed when calling the API via ``POST``."""

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
