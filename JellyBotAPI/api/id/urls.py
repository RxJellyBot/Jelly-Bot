from django.conf.urls import url

from .channel import ChannelDataQueryView

urlpatterns = [
    url(r'ch$', ChannelDataQueryView.as_view(), name='api.id.channel')
]
