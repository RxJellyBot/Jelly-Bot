from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBot.views import render_template
from JellyBot.components.mixin import LoginRequiredMixin
from msghandle.botcmd.command import cmd_uintg


class UserIdentityIntegrateView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(
            request, _("Integrate Identity"), "account/integrate.html", {"cmd_code": cmd_uintg.main_cmd_code})
