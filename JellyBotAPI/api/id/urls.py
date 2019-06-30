from django.urls import path

from .channel import ChannelDataQueryView, ChannelIssueRegistrationTokenView

urlpatterns = [
    path('ch/data', ChannelDataQueryView.as_view(), name='api.id.channel.data'),
    path('ch/reg/issue', ChannelIssueRegistrationTokenView.as_view(), name='api.id.channel.register_token')
]
