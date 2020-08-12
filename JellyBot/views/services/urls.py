from django.urls import path

from .line_sticker import (
    LineStickerAnimatedGifDownloadView, LineStickerAnimatedFramesDownloadView, LineStickerAnimatedPngDownloadView
)
from .shorturl import ShortUrlMainView
from .maskfinder import MaskFinderMainView

urlpatterns = [
    path(
        'linesticker/<int:pack_id>/<int:sticker_id>/sticker.gif',
        LineStickerAnimatedGifDownloadView.as_view(),
        name="service.linesticker.animated.gif"
    ),
    path(
        'linesticker/<int:pack_id>/<int:sticker_id>/frames.zip',
        LineStickerAnimatedFramesDownloadView.as_view(),
        name="service.linesticker.animated.frames"
    ),
    path(
        'linesticker/<int:pack_id>/<int:sticker_id>/sticker.png',
        LineStickerAnimatedPngDownloadView.as_view(),
        name="service.linesticker.animated.apng"
    ),
    path('shorturl/', ShortUrlMainView.as_view(), name="service.shorturl"),
    path('maskfinder/', MaskFinderMainView.as_view(), name="service.maskfinder"),
]
