from django.conf.urls import url

from JellyBotAPI.views.account import AccountMainPageView


urlpatterns = [
    url(r'', AccountMainPageView.as_view(), name="account.main")
]
