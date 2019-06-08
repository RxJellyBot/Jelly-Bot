from django.urls import path

from .main import AccountMainPageView
from .control import AccountLogoutView


urlpatterns = [
    path('', AccountMainPageView.as_view(), name='account.main'),
    path('logout', AccountLogoutView.as_view(), name='account.logout')
]
