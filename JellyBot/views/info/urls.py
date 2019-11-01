from django.urls import path

from JellyBot.keys import URLPathParameter

from .channel import ChannelInfoView, ChannelInfoSearchView
from .profile import ProfileInfoView

urlpatterns = [
    path(f'channel/<str:{URLPathParameter.ChannelOid}>/', ChannelInfoView.as_view(), name="info.channel"),
    path('channel/', ChannelInfoSearchView.as_view(), name="info.channel.search"),
    path(f'profile/<str:{URLPathParameter.ProfileOid}>/', ProfileInfoView.as_view(), name="info.profile"),
]
