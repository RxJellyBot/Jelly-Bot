from bson import ObjectId
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils import safe_cast
from mongodb.factory import ProfileManager
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


class AccountChannelListView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        channel_conn_list = ProfileManager.get_user_channel_profiles(get_root_oid(request))

        return render_template(
            self.request, _("Channel Management"), "account/channel/list.html", {
                "channel_conn_list": channel_conn_list
            })


class AccountChannelManagingView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyTypeChecker
    def get(self, request, **kwargs):
        channel_oid = safe_cast(kwargs["channel_oid"], ObjectId)
        # FIXME: [Priority 1]
        #   - Add channel privacy settings
        #   - Add logic to `ProfileManager.get_user_profiles` that
        #       - If the channel is set to private: User needs to be in the channel
        #       - If the channel is set to public: `channel_oid` needs to be valid only
        u_profs = ProfileManager.get_user_profiles(channel_oid, get_root_oid(request))

        if u_profs:
            return render_template(
                self.request, _(f"Channel Management - {channel_oid}"), "account/channel/manage.html", {
                    "user_profiles": u_profs,
                    "perm_sum": ProfileManager.get_permissions(u_profs),
                    "channel_oid": channel_oid
                }, nav_param=kwargs)
        else:
            return render_template(self.request, _("Profile Link Not Found"), "err/account/proflink_not_found.html", {
                "channel_oid": channel_oid
            })


class AccountProfileView(LoginRequiredMixin, TemplateResponseMixin, View):
    def get(self, request, **kwargs):
        profile_oid = safe_cast(kwargs["profile_oid"], ObjectId)
        profile_data = ProfileManager.get_profile(profile_oid)

        if profile_data:
            return render_template(
                self.request, _(f"Profile Info - {profile_data.name}"), "account/channel/profile.html", {
                    "profile_data": profile_data,
                }, nav_param=kwargs)
        else:
            return render_template(self.request, _("Profile Not Found"), "err/account/profile_not_found.html", {
                "profile_oid": profile_oid
            })
