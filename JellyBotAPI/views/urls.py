from django.conf.urls import url

from JellyBotAPI.views.index import HomePageView
from JellyBotAPI.views.regapi import RegisterAPIUserView
from JellyBotAPI.views.about import AboutView


urlpatterns = [
    url(r'^$', HomePageView.as_view(), name="page.home"),
    url(r'^login/$', RegisterAPIUserView.as_view(), name="page.login"),
    url(r'^about/$', AboutView.as_view(), name="page.about")
]
