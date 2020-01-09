from typing import Optional

from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from JellyBot.views import render_template
from JellyBot.utils import get_root_oid
from JellyBot.components.mixin import ChannelOidRequiredMixin
from models import ChannelCollectionModel
from mongodb.factory import ProfileManager, ChannelCollectionManager, BotFeatureUsageDataManager
from mongodb.helper import MessageStatsDataProcessor, IdentitySearcher


class ChannelInfoView(ChannelOidRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        channel_data = self.get_channel_data(*args, **kwargs)

        chcoll_data: Optional[ChannelCollectionModel] = \
            ChannelCollectionManager.get_chcoll_child_channel(channel_data.model.id)

        msgdata_1d = MessageStatsDataProcessor.get_user_channel_messages(channel_data.model, 24)
        msgdata_7d = MessageStatsDataProcessor.get_user_channel_messages(channel_data.model, 168)

        channel_name = channel_data.model.get_channel_name(get_root_oid(request))

        return render_template(
            self.request, _("Channel Info - {}").format(channel_name), "info/channel/main.html",
            {
                "channel_name": channel_name,
                "channel_data": channel_data.model,
                "chcoll_data": chcoll_data,
                "user_message_data1d": msgdata_1d,
                "msg_count1d": msgdata_1d.msg_count,
                "user_message_data7d": msgdata_7d,
                "msg_count7d": msgdata_7d.msg_count,
                "manageable": bool(
                    ProfileManager.get_user_profiles(channel_data.model.id, get_root_oid(request))),
                "bot_usage_7d": BotFeatureUsageDataManager.get_channel_usage(channel_data.model.id, 168),
                "bot_usage_all": BotFeatureUsageDataManager.get_channel_usage(channel_data.model.id)
            },
            nav_param=kwargs)


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
