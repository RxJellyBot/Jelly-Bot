from django.urls import path

from .shorturl import ShortUrlShortenView, ShortUrlTargetChangeView

urlpatterns = [
    path('shorturl/shorten', ShortUrlShortenView.as_view(), name='api.service.shorturl.short'),
    path('shorturl/update', ShortUrlTargetChangeView.as_view(), name='api.service.shorturl.update')
]
