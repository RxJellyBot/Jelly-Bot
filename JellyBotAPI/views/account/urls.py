from django.urls import path

from .main import AccountMainPageView
from .control import AccountLogoutView, AccountSettingsPageView


urlpatterns = [
    path('', AccountMainPageView.as_view(), name='account.main'),
    path('logout', AccountLogoutView.as_view(), name='account.logout'),
    path('settings', AccountSettingsPageView.as_view(), name='account.settings')
]
