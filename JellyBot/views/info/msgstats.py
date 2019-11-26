from typing import Optional

from bson import ObjectId
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.components import get_root_oid
from extutils import safe_cast
from flags import WebsiteError
from models import ChannelModel, ChannelCollectionModel
from mongodb.factory import ChannelManager, ProfileManager, MessageRecordStatisticsManager
from mongodb.helper import MessageStatsDataProcessor, IdentitySearcher


class ChannelMessageStatsView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        # `kwargs` will be used as `nav_param` so extract channel_oid from `kwargs` instead of creating param.

        # `channel_oid` may be misformatted.
        # If so, `safe_cast` will yield `None` while the original parameter needs to be kept for the case of not found.
        channel_oid_str = kwargs.get("channel_oid", "")
        channel_oid = safe_cast(channel_oid_str, ObjectId)

        channel_data: Optional[ChannelModel] = ChannelManager.get_channel_oid(channel_oid)

        if not channel_data:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_NOT_FOUND, {"channel_oid": channel_oid_str}, nav_param=kwargs)

        hours_within = safe_cast(request.GET.get("hours_within"), int) or ""

        msg_intvflow_data = MessageRecordStatisticsManager.hourly_interval_message_count(
                    channel_oid, hours_within)

        user_channel_messages = MessageStatsDataProcessor.get_user_channel_messages(channel_data, hours_within)

        channel_members = ProfileManager.get_channel_members(channel_oid)  # Reserved for per member analysis

        return render_template(
            self.request, _("Channel Message Stats - {}").format(channel_oid), "info/msgstats/main.html",
            {
                "ch_name": channel_data.get_channel_name(get_root_oid(request)),
                "channel_data": channel_data,
                "hr_range": hours_within or msg_intvflow_data.hr_range,
                "msg_intvflow_data": msg_intvflow_data,
                "channel_user_msg": user_channel_messages
            },
            nav_param=kwargs)
