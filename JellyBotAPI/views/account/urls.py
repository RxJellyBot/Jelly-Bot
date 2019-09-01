from django.urls import path

from .main import AccountMainPageView
from .control import AccountLoginView, AccountLogoutView, AccountSettingsPageView
from .channel import (
    AccountChannelRegistrationView, AccountChannelListView, AccountChannelManagingView, AccountProfileView
)

urlpatterns = [
    path('', AccountMainPageView.as_view(), name='account.main'),
    path('login', AccountLoginView.as_view(), name="account.login"),
    path('logout', AccountLogoutView.as_view(), name='account.logout'),
    path('settings', AccountSettingsPageView.as_view(), name='account.settings'),
    path('channel/register', AccountChannelRegistrationView.as_view(), name='account.channel.connect'),
    path('channel/manage', AccountChannelListView.as_view(), name='account.channel.list'),
    path('channel/manage/<str:channel_oid>', AccountChannelManagingView.as_view(), name='account.channel.manage'),
    path('profile/<str:profile_oid>', AccountProfileView.as_view(), name='account.profile')
]
