from django.urls import path

from JellyBotAPI.views.ar import AutoReplyAddView, MainPageView

urlpatterns = [
    path('', MainPageView.as_view(), name="page.ar.main"),
    path('add/', AutoReplyAddView.as_view(), name="page.ar.add")
]
