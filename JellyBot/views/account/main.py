from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.dt import now_utc_aware, t_delta_str
from JellyBot import keys
from JellyBot.views import render_template
from JellyBot.components.mixin import LoginRequiredMixin
from mongodb.factory import RootUserManager, ExecodeManager


class AccountMainPageView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        u_data = RootUserManager.get_root_data_api_token(self.request.COOKIES[keys.Cookies.USER_TOKEN])
        excde_list = ExecodeManager.get_queued_execodes(u_data.model.id)

        return render_template(
            self.request, _("Account Home"), "account/main.html",
            {"root_data": u_data.model, "api_user_data": u_data.model_api,
             "execode_list": excde_list, "onplat_user_data_list": u_data.model_onplat_list,
             "reg_time_str": t_delta_str(now_utc_aware() - u_data.model.id.generation_time)})
