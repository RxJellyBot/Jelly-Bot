from django.urls import path

from .main import AccountMainPageView
from .control import AccountLoginView, AccountLogoutView, AccountSettingsPageView
from .integrate import UserIdentityIntegrateView
from .channel import (
    AccountChannelRegistrationView, AccountChannelListView, AccountChannelManagingView
)

urlpatterns = [
    path('', AccountMainPageView.as_view(), name='account.main'),
    path('login/', AccountLoginView.as_view(), name="account.login"),
    path('logout/', AccountLogoutView.as_view(), name='account.logout'),
    path('settings/', AccountSettingsPageView.as_view(), name='account.settings'),
    path('integrate/', UserIdentityIntegrateView.as_view(), name='account.integrate'),
    path('channel/register/', AccountChannelRegistrationView.as_view(), name='account.channel.connect'),
    path('channel/manage/', AccountChannelListView.as_view(), name='account.channel.list'),
    path('channel/manage/<str:channel_oid>/', AccountChannelManagingView.as_view(), name='account.channel.manage'),
]
