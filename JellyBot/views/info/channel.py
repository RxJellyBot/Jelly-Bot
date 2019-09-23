from bson import ObjectId
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBot.views import render_template
from JellyBot.components import get_root_oid
from extutils import safe_cast
from mongodb.factory import ChannelManager, ProfileManager


class ChannelInfoView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        # `kwargs` will be used as `nav_param` so extract channel_oid from `kwargs` instead of creating param.

        # `channel_oid` may be misformatted.
        # If so, `safe_cast` will yield `None` while the original parameter needs to be kept for the case of not found.
        channel_oid_str = kwargs.get("channel_oid", "")
        channel_oid = safe_cast(channel_oid_str, ObjectId)

        c_prof = ChannelManager.get_channel_oid(channel_oid)

        if c_prof:
            return render_template(
                self.request, _("Channel Info - {}").format(channel_oid), "info/channel.html",
                {
                    "channel_data": c_prof,
                    "manageable": bool(ProfileManager.get_user_profiles(channel_oid, get_root_oid(request)))
                },
                nav_param=kwargs)
        else:
            return render_template(
                self.request, _("Channel Not Found"), "err/info/channel_not_found.html",
                {
                    "channel_oid": channel_oid_str
                },
                nav_param=kwargs)


class ChannelInfoSearchView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        # INCOMPLETE: Channel Info query page - .../info/channel for users to search channel info
        #   Allow to search channel by various conditions (ID, profile names, messages...etc.)
        return render_template(
            self.request, _("Channel Info Search"), "info/channel_search.html", nav_param=kwargs)
