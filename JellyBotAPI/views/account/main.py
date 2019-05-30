from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBotAPI import keys
from JellyBotAPI.views import render_template
from JellyBotAPI.components.mixin import LoginRequiredMixin
from mongodb.factory import MixedUserManager


class AccountMainPageView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, context, **response_kwargs):
        u_data = MixedUserManager.get_user_data_api_token(self.request.COOKIES[keys.USER_TOKEN])

        return render_template(
            self.request, "account/main.html",  {"title": _("Account Home"), "api_user_data": u_data})
