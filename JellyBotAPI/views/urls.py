from django.urls import path, include

from JellyBotAPI.views.index import HomePageView
from JellyBotAPI.views.about import AboutView


urlpatterns = [
    path('', HomePageView.as_view(), name="page.home"),
    path('about/', AboutView.as_view(), name="page.about"),
    path('account/', include('JellyBotAPI.views.account.urls')),
    path('ar/', include('JellyBotAPI.views.ar.urls')),
    path('doc/', include('JellyBotAPI.views.doc.urls')),
    path('info/', include('JellyBotAPI.views.info.urls')),
]
