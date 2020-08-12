from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from flags import Execode
from JellyBot.views import render_template
from JellyBot.components.mixin import LoginRequiredMixin
from msghandle.botcmd.command import cmd_uintg


class UserDataIntegrateView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        return render_template(
            request, _("Integrate User Data"), "account/integrate.html",
            {
                "cmd_code": cmd_uintg.main_cmd_code,
                "cmd_usage": cmd_uintg.get_usage(),
                "excde_type_code": Execode.INTEGRATE_USER_DATA.code
            })
