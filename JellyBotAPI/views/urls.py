from django.urls import path

from JellyBotAPI.views.index import HomePageView
from JellyBotAPI.views.regapi import RegisterAPIUserView
from JellyBotAPI.views.about import AboutView


urlpatterns = [
    path('', HomePageView.as_view(), name="page.home"),
    path('login/', RegisterAPIUserView.as_view(), name="page.login"),
    path('about/', AboutView.as_view(), name="page.about")
]
