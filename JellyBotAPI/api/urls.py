from django.urls import path
from django.urls import include

from .status import status_check

urlpatterns = [
    path('status/', status_check, name='JellyBotAPI.api.status'),
    path('ar/', include('JellyBotAPI.api.ar.urls')),
    path('id/', include('JellyBotAPI.api.id.urls')),
]
