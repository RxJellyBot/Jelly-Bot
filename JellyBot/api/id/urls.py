from django.urls import path

from .channel import (
    ChannelDataQueryView, ChannelIssueRegistrationExecodeView, ChannelNameChangeView, ChannelStarChangeView
)
from .perm import PermissionQueryView

urlpatterns = [
    path('ch/data', ChannelDataQueryView.as_view(), name='api.id.channel.data'),
    path('ch/reg/issue', ChannelIssueRegistrationExecodeView.as_view(), name='api.id.channel.register_execode'),
    path('ch/name-change', ChannelNameChangeView.as_view(), name='api.id.channel.name_change'),
    path('ch/star-change', ChannelStarChangeView.as_view(), name='api.id.channel.star_change'),
    path('perm', PermissionQueryView.as_view(), name='api.id.perm')
]
