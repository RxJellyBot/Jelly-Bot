from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.linesticker import LineStickerUtils


class LineStickerPackageDownloadView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id, *args, **kwargs):
        binary_io = LineStickerUtils.get_downloaded_sticker_pack(pack_id)

        if not binary_io:
            return HttpResponse(status=404)

        return FileResponse(binary_io, as_attachment=True)


class LineStickerAnimatedPngDownloadView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id, sticker_id, *args, **kwargs):
        return redirect(LineStickerUtils.get_apng_url(pack_id, sticker_id), permanent=True)


class LineStickerAnimatedGifDownloadView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id, sticker_id, *args, **kwargs):
        binary_io = LineStickerUtils.get_downloaded_animated(pack_id, sticker_id)

        if not binary_io:
            return HttpResponse(status=404)

        return FileResponse(binary_io, as_attachment=True)


class LineStickerAnimatedFramesDownloadView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id, sticker_id, *args, **kwargs):
        binary_io = LineStickerUtils.get_downloaded_apng_frames(pack_id, sticker_id)

        if not binary_io:
            return HttpResponse(status=404)

        return FileResponse(binary_io, as_attachment=True)
