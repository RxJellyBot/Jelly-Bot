from django.urls import path
from django.urls import include

from .status import status_check
from .execode import ExecodeCompleteView, ExecodeListView
from .webhook import WebhookLineView

urlpatterns = [
    path('status/', status_check, name='JellyBot.api.status'),
    path('ar/', include('JellyBot.api.ar.urls')),
    path('id/', include('JellyBot.api.id.urls')),
    path('service/', include('JellyBot.api.services.urls')),
    path('execode', ExecodeCompleteView.as_view(), name="api.execode.complete"),
    path('execode/list', ExecodeListView.as_view(), name="api.execode.list"),
    path('webhook/line', WebhookLineView.as_view(), name="api.webhook.line")
]
