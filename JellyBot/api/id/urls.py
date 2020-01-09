from django.urls import path

from .channel import (
    ChannelDataQueryView, ChannelIssueRegistrationExecodeView, ChannelNameChangeView, ChannelStarChangeView
)
from .prof import PermissionQueryView, ProfileDetachView, ProfileNameCheckView, ProfileAttachView

urlpatterns = [
    path('ch/data', ChannelDataQueryView.as_view(), name='api.id.channel.data'),
    path('ch/reg/issue', ChannelIssueRegistrationExecodeView.as_view(), name='api.id.channel.register_execode'),
    path('ch/name-change', ChannelNameChangeView.as_view(), name='api.id.channel.name_change'),
    path('ch/star-change', ChannelStarChangeView.as_view(), name='api.id.channel.star_change'),
    path('prof/perm', PermissionQueryView.as_view(), name='api.id.perm'),
    path('prof/detach', ProfileDetachView.as_view(), name='api.id.profile.detach'),
    path('prof/attach', ProfileAttachView.as_view(), name='api.id.profile.attach'),
    path('prof/name', ProfileNameCheckView.as_view(), name='api.id.profile.name')
]
