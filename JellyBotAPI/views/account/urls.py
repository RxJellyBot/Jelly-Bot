from django.urls import path

from .main import AccountMainPageView
from .control import AccountLogoutView, AccountSettingsPageView
from .channel import AccountChannelRegistrationView, AccountChannelManagingView

urlpatterns = [
    path('', AccountMainPageView.as_view(), name='account.main'),
    path('logout', AccountLogoutView.as_view(), name='account.logout'),
    path('settings', AccountSettingsPageView.as_view(), name='account.settings'),
    path('channel/register', AccountChannelRegistrationView.as_view(), name='account.channel.connect'),
    path('channel/manage', AccountChannelManagingView.as_view(), name='account.channel.manage')
]
