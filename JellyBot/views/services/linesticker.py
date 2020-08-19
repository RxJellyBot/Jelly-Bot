"""Views for LINE sticker downloader."""
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.linesticker import LineStickerUtils
from JellyBot.views import render_template


class LineStickerDownloadView(TemplateResponseMixin, View):
    """View of LINE sticker downloader UI."""

    def get(self, request):
        """Render the webpage for LINE sticker downloader UI."""
        context = {}
        context["pack_url"] = pack_url = request.GET.get("url", "")
        context["pack_meta"] = pack_meta = LineStickerUtils.get_pack_meta_from_url(pack_url)

        if pack_url and not pack_meta:
            messages.warning(request, "Unable to get the LINE sticker package ID. "
                                      "Check the format of the URL to be parsed.")

        return render_template(self.request, _("LINE Sticker Downloader"), "services/linesticker.html", context)


class LineStickerPackageDownloadView(TemplateResponseMixin, View):
    """View to download a LINE sticker package."""

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id):
        """Download the LINE sticker package file to the user's end."""
        binary_io = LineStickerUtils.get_downloaded_sticker_pack(pack_id)

        if not binary_io:
            return HttpResponse(status=404)

        return FileResponse(binary_io, as_attachment=True)


class LineStickerAnimatedPngRedirectView(TemplateResponseMixin, View):
    """View to see the apng of an animated sticker."""

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id, sticker_id):
        """Redirect the user to the apng page of an animated sticker."""
        return redirect(LineStickerUtils.get_apng_url(pack_id, sticker_id), permanent=True)


class LineStickerAnimatedGifDownloadView(TemplateResponseMixin, View):
    """View to download an animated sticker as gif."""

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id, sticker_id):
        """Download the gif file of an animated sticker to the user's end."""
        binary_io = LineStickerUtils.get_downloaded_animated(pack_id, sticker_id)

        if not binary_io:
            return HttpResponse(status=404)

        return FileResponse(binary_io, as_attachment=True)


class LineStickerAnimatedFramesDownloadView(TemplateResponseMixin, View):
    """View to download the frames of an animated sitcker."""

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, pack_id, sticker_id):
        """Download the frames of an animated sticker as a zip file to the user's end."""
        binary_io = LineStickerUtils.get_downloaded_apng_frames(pack_id, sticker_id)

        if not binary_io:
            return HttpResponse(status=404)

        return FileResponse(binary_io, as_attachment=True)
