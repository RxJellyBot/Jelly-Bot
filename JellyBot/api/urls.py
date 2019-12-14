from django.urls import path
from django.urls import include

from .execode import ExecodeCompleteView, ExecodeListView
from .webhook import WebhookLineView

urlpatterns = [
    path('ar/', include('JellyBot.api.ar.urls')),
    path('id/', include('JellyBot.api.id.urls')),
    path('service/', include('JellyBot.api.services.urls')),
    path('execode', ExecodeCompleteView.as_view(), name="api.execode.complete"),
    path('execode/list', ExecodeListView.as_view(), name="api.execode.list"),
    path('webhook/line', WebhookLineView.as_view(), name="api.webhook.line")
]
