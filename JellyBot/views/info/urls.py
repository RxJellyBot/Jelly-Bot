from django.urls import path

from .channel import ChannelInfoView, ChannelInfoSearchView
from .profile import ProfileInfoView

urlpatterns = [
    path(f'channel/<str:channel_oid>/', ChannelInfoView.as_view(), name="info.channel"),
    path('channel/', ChannelInfoSearchView.as_view(), name="info.channel.search"),
    path(f'profile/<str:profile_oid>/', ProfileInfoView.as_view(), name="info.profile"),
]
