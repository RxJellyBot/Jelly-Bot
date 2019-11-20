from django.urls import path

from .shorturl import ShortUrlMainView

urlpatterns = [
    path('shorturl/', ShortUrlMainView.as_view(), name="service.shorturl"),
]
