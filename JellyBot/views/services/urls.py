from django.urls import path

from .shorturl import ShortUrlMainView
from .maskfinder import MaskFinderMainView

urlpatterns = [
    path('shorturl/', ShortUrlMainView.as_view(), name="service.shorturl"),
    path('maskfinder/', MaskFinderMainView.as_view(), name="service.maskfinder"),
]
