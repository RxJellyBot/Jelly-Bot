from bson import ObjectId

from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils import safe_cast
from flags import WebsiteError
from mongodb.factory import ProfileManager, ChannelManager
from msghandle.botcmd.command import cmd_id
from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.components import get_root_oid
from JellyBot.components.mixin import LoginRequiredMixin
from JellyBot.systemconfig import TokenAction


class AccountChannelRegistrationView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(
            self.request, _("Channel Register"), "account/channel/register.html",
            {"register_cooldown": TokenAction.ChannelRegisterTokenCooldownSeconds})


class AccountChannelListView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)

        channel_conn_list = ProfileManager.get_user_channel_profiles(root_oid)

        return render_template(
            self.request, _("Channel Management"), "account/channel/list.html", {
                "channel_conn_list": channel_conn_list,
                "bot_cmd_info_code": cmd_id.main_cmd_code
            })


class AccountChannelManagingView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyTypeChecker, PyUnusedLocal
    def get(self, request, *args, **kwargs):
        # `kwargs` will be used as `nav_param` so extract channel_oid from `kwargs` instead of creating param.
        channel_oid_str = kwargs.get("channel_oid", "")
        channel_oid = safe_cast(channel_oid_str, ObjectId)
        u_profs = ProfileManager.get_user_profiles(channel_oid, get_root_oid(request))

        if u_profs:
            return render_template(
                self.request, _("Channel Management - {}").format(channel_oid), "account/channel/manage.html", {
                    "user_profiles": u_profs,
                    "perm_sum": ProfileManager.get_permissions(u_profs),
                    "channel_oid": channel_oid
                }, nav_param=kwargs)
        else:
            c_prof = ChannelManager.get_channel_oid(channel_oid)

            if c_prof:
                return redirect("info.channel")
            else:
                return WebsiteErrorView.website_error(
                    request, WebsiteError.PROFILE_LINK_NOT_FOUND, {"channel_oid": channel_oid_str})
