from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from mongodb.factory import PermissionManager
from JellyBotAPI.views import render_template
from JellyBotAPI.components import get_root_oid
from JellyBotAPI.components.mixin import LoginRequiredMixin
from JellyBotAPI.SystemConfig import TokenAction


class AccountChannelRegistrationView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(
            self.request, _("Channel Register"), "account/channel/register.html",
            {"register_cooldown": TokenAction.ChannelRegisterTokenCooldownSeconds})


class AccountChannelManagingView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        channel_conn_list = PermissionManager.get_user_channel_profile_list(get_root_oid(self.request))

        return render_template(
            self.request, _("Channel Management"), "account/channel/manage.html", {
                "channel_conn_list": channel_conn_list
            })
