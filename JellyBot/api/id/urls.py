from django.urls import path

from .channel import ChannelDataQueryView, ChannelIssueRegistrationTokenView, ChannelNameChangeView
from .perm import PermissionQueryView

urlpatterns = [
    path('ch/data', ChannelDataQueryView.as_view(), name='api.id.channel.data'),
    path('ch/reg/issue', ChannelIssueRegistrationTokenView.as_view(), name='api.id.channel.register_token'),
    path('ch/name-change', ChannelNameChangeView.as_view(), name='api.id.channel.name_change'),
    path('perm', PermissionQueryView.as_view(), name='api.id.perm')
]
