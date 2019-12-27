from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.utils import get_root_oid, get_channel_data
from JellyBot.systemconfig import Website
from extutils import safe_cast

from flags import WebsiteError
from models import ChannelProfileConnectionModel
from mongodb.helper import MessageStatsDataProcessor
from mongodb.factory import ProfileManager


class RecentMessagesView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        channel_data = get_channel_data(kwargs)

        # Check if the channel data exists
        if not channel_data.ok:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_NOT_FOUND, {"channel_oid": channel_data.oid_org}, nav_param=kwargs)

        # Check if the user is in the channel
        root_oid = get_root_oid(request)
        profs = ProfileManager.get_user_profiles(channel_data.model.id, root_oid)
        if not profs or profs == ChannelProfileConnectionModel.ProfileOids.none_obj():
            return WebsiteErrorView.website_error(
                request, WebsiteError.NOT_IN_THE_CHANNEL, {"channel_oid": channel_data.oid_org}, nav_param=kwargs)

        # Process the necessary data
        channel_name = channel_data.model.get_channel_name(root_oid)

        limit = safe_cast(request.GET.get("limit"), int)
        if limit:
            limit = min(limit, Website.RecentActivity.MaxMessageCount)
        else:
            limit = Website.RecentActivity.MaxMessageCount

        ctxt = {
            "channel_name": channel_name,
            "channel_data": channel_data.model,
            "recent_msg_limit": limit or "",
            "recent_msg_limit_max": Website.RecentActivity.MaxMessageCount,
            "recent_msg_data": MessageStatsDataProcessor.get_recent_messages(channel_data.model, limit)
        }

        return render_template(
            self.request, _("Recent Messages - {}").format(channel_name),
            "info/recent/message.html", ctxt, nav_param=kwargs)
