from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.linesticker import LineStickerUtils
from JellyBot.views import render_template


class LineStickerDownloadView(TemplateResponseMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        context["pack_url"] = pack_url = request.GET.get("url", "")
        context["pack_meta"] = pack_meta = LineStickerUtils.get_pack_meta_from_url(pack_url)

        if pack_url and not pack_meta:
            messages.warning(request, "Unable to get the LINE sticker package ID. "
                                      "Check the format of the URL to be parsed.")

        return render_template(self.request, _("LINE Sticker Downloader"), "services/linesticker.html", context)


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
