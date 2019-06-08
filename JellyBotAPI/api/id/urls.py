from django.urls import path

from .channel import ChannelDataQueryView

urlpatterns = [
    path('ch', ChannelDataQueryView.as_view(), name='api.id.channel')
]
