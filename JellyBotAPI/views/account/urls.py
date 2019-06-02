from django.urls import path

from JellyBotAPI.views.account import AccountMainPageView


urlpatterns = [
    path('', AccountMainPageView.as_view(), name="account.main")
]
