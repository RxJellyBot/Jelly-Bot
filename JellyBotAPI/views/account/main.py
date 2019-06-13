from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBotAPI import keys
from JellyBotAPI.views import render_template
from JellyBotAPI.components.mixin import LoginRequiredMixin
from mongodb.factory import MixedUserManager, TokenActionManager


class AccountMainPageView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        u_data = MixedUserManager.get_user_data_api_token(self.request.COOKIES[keys.USER_TOKEN]).model
        tkact_list = TokenActionManager.get_queued_actions(u_data.id.value)

        return render_template(
            self.request, _("Account Home"), "account/main.html", {"api_user_data": u_data,
                                                                   "tkact_list": tkact_list})
