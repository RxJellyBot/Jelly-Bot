from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBotAPI.views import render_template
from JellyBotAPI.components.mixin import LoginRequiredMixin


class AccountChannelRegistrationView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(
            self.request, _("Channel Register"), "account/channel/register.html")


class AccountChannelManagingView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(
            self.request, _("Channel Management"), "account/channel/manage.html")
