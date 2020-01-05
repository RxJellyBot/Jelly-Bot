from django.urls import path

from .main import AccountMainPageView
from .control import AccountLoginView, AccountLogoutView, AccountSettingsPageView
from .integrate import UserDataIntegrateView
from .channel import (
    AccountChannelRegistrationView, AccountChannelListView, AccountChannelManagingView
)
from .prof import ProfileCreateView

urlpatterns = [
    path('', AccountMainPageView.as_view(), name='account.main'),
    path('login/', AccountLoginView.as_view(), name="account.login"),
    path('logout/', AccountLogoutView.as_view(), name='account.logout'),
    path('settings/', AccountSettingsPageView.as_view(), name='account.settings'),
    path('integrate/', UserDataIntegrateView.as_view(), name='account.integrate'),
    path('channel/register/', AccountChannelRegistrationView.as_view(), name='account.channel.connect'),
    path('channel/manage/', AccountChannelListView.as_view(), name='account.channel.list'),
    path('channel/manage/<str:channel_oid>/', AccountChannelManagingView.as_view(), name='account.channel.manage'),
    path('profile/<str:channel_oid>/create/', ProfileCreateView.as_view(), name='account.profile.create'),
]
