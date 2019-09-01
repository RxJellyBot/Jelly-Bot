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
    def get(self, request, **kwargs):
        # FIXME: [Priority 1]
        #  render individual channel managing page depends on the user's permissions based on the profile
        channel_oid = safe_cast(kwargs["channel_oid"], ObjectId)
        u_prof = ProfileManager.get_user_profiles(channel_oid, get_root_oid(request))

        # FIXME: [Priority 1]
        #   - `u_prof` is not the `list` of `ChannelProfileModel`

        if u_prof:
            return render_template(
                self.request, _("Channel Management"), "account/channel/manage.html", {
                    "user_profiles": u_prof,
                    "channel_oid": channel_oid,
                    # Translators: Separator for the profiles in channel management page
                    "prof_separator": _(", ")
                }, nav_param=kwargs)
        else:
            return render_template(self.request, _("Profile Not Found"), "err/account/profile_not_found.html", {
                "channel_oid": channel_oid
            })
