from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.maskfinder import get_results
from JellyBot.views import render_template
from JellyBot.systemconfig import ExtraService


class MaskFinderMainView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        context = {
            "target_range_mi": ExtraService.Maskfinder.TargetRangeMi
        }
        zip_code = request.GET.get("zip")

        if zip_code:
            context["zip_code"] = zip_code
            context["results"] = get_results(zip_code, ExtraService.Maskfinder.TargetRangeMi)

        return render_template(self.request, _("Maskfinder (US Only)"), "services/maskfinder/main.html", context)
