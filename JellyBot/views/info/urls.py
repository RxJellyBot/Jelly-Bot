from django.urls import path

from .channel import ChannelInfoView, ChannelInfoSearchView
from .chcoll import ChannelCollectionInfoView
from .profile import ProfileInfoView
from .msgstats import ChannelMessageStatsView
from .botstats import ChannelBotUsageStatsView


urlpatterns = [
    path('channel/', ChannelInfoSearchView.as_view(), name="info.channel.search"),
    path(f'channel/<str:channel_oid>/', ChannelInfoView.as_view(), name="info.channel"),
    path(f'channel/<str:channel_oid>/msgstats/', ChannelMessageStatsView.as_view(), name="info.channel.msgstats"),
    path(f'channel/<str:channel_oid>/botstats/', ChannelBotUsageStatsView.as_view(), name="info.channel.botstats"),
    path(f'chcoll/<str:chcoll_oid>/', ChannelCollectionInfoView.as_view(), name="info.chcoll"),
    path(f'profile/<str:profile_oid>/', ProfileInfoView.as_view(), name="info.profile"),
]
