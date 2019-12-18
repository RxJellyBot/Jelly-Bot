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
from mongodb.factory import ChannelManager, ProfileManager, ChannelCollectionManager, BotFeatureUsageDataManager
from mongodb.helper import MessageStatsDataProcessor, IdentitySearcher


class ChannelInfoView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        # `kwargs` will be used as `nav_param` so extract channel_oid from `kwargs` instead of creating param.

        # `channel_oid` may be misformatted.
        # If so, `safe_cast` will yield `None` while the original parameter needs to be kept for the case of not found.
        channel_oid_str = kwargs.get("channel_oid", "")
        channel_oid = safe_cast(channel_oid_str, ObjectId)

        channel_data: Optional[ChannelModel] = ChannelManager.get_channel_oid(channel_oid)

        if channel_data:
            chcoll_data: Optional[ChannelCollectionModel] = \
                ChannelCollectionManager.get_chcoll_child_channel(channel_data.id)

            msgdata_1d = MessageStatsDataProcessor.get_user_channel_messages(channel_data, 24)
            msgdata_7d = MessageStatsDataProcessor.get_user_channel_messages(channel_data, 168)

            return render_template(
                self.request, _("Channel Info - {}").format(channel_oid), "info/channel/main.html",
                {
                    "ch_name": channel_data.get_channel_name(get_root_oid(request)),
                    "channel_data": channel_data,
                    "chcoll_data": chcoll_data,
                    "user_message_data1d": msgdata_1d.member_stats,
                    "msg_count1d": msgdata_1d.msg_count,
                    "user_message_data7d": msgdata_7d.member_stats,
                    "msg_count7d": msgdata_7d.msg_count,
                    "manageable": bool(
                        ProfileManager.get_user_profiles(channel_oid, get_root_oid(request))),
                    "bot_usage_7d": BotFeatureUsageDataManager.get_channel_usage(channel_oid, 168),
                    "bot_usage_all": BotFeatureUsageDataManager.get_channel_usage(channel_oid)
                },
                nav_param=kwargs)
        else:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_NOT_FOUND, {"channel_oid": channel_oid_str}, nav_param=kwargs)


class ChannelInfoSearchView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        keyword = request.GET.get("w", "")
        channel_list = []

        if keyword:
            channel_list = IdentitySearcher.search_channel(keyword, get_root_oid(request))

        return render_template(
            self.request, _("Channel Info Search"), "info/channel/search.html",
            {"channel_list": channel_list, "keyword": keyword}, nav_param=kwargs)
