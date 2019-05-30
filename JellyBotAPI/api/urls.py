from django.conf.urls import url
from django.urls import include

from .status import status_check

urlpatterns = [
    url(r'status/', status_check, name='api.status'),
    url(r'ar/', include('JellyBotAPI.api.ar.urls')),
]
