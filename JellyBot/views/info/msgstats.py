from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional

from bson import ObjectId
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.timezone import get_current_timezone

from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.components import get_root_oid
from extutils import safe_cast
from flags import WebsiteError
from models import ChannelModel
from mongodb.factory import ChannelManager, MessageRecordStatisticsManager
from mongodb.helper import MessageStatsDataProcessor

KEY_MSG_INTV_FLOW = "msg_intvflow_data"
KEY_MSG_DAILY = "msg_daily_data"
KEY_MSG_USER_CHANNEL = "channel_user_msg"


def _msg_intv_flow_(channel_oid, hours_within):
    return KEY_MSG_INTV_FLOW, MessageRecordStatisticsManager.hourly_interval_message_count(
        channel_oid, hours_within)


def _msg_daily_(channel_oid, hours_within, tzinfo):
    return KEY_MSG_DAILY, MessageRecordStatisticsManager.daily_message_count(
        channel_oid, hours_within, tzinfo)


def _channel_user_msg_(channel_data, hours_within):
    return KEY_MSG_USER_CHANNEL, MessageStatsDataProcessor.get_user_channel_messages(channel_data, hours_within)


def get_msg_stats_data_package(channel_data, hours_within, tzinfo):
    ret = {}

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="MsgStats") as executor:
        futures = [executor.submit(_msg_intv_flow_, channel_data.id, hours_within),
                   executor.submit(_msg_daily_, channel_data.id, hours_within, tzinfo),
                   executor.submit(_channel_user_msg_, channel_data, hours_within)]

        # Non-lock call & Free resources when execution is done
        executor.shutdown(False)

        for completed in futures:
            key, result = completed.result()

            ret[key] = result

    return ret


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

        # channel_members = ProfileManager.get_channel_members(channel_oid)  # Reserved for per member analysis

        pkg = get_msg_stats_data_package(channel_data, hours_within, get_current_timezone())
        ctxt = {
            "ch_name": channel_data.get_channel_name(get_root_oid(request)),
            "channel_data": channel_data,
            "hr_range": hours_within or pkg[KEY_MSG_INTV_FLOW].hr_range,
        }
        ctxt.update(pkg)

        return render_template(
            self.request, _("Channel Message Stats - {}").format(channel_oid),
            "info/msgstats/main.html", ctxt, nav_param=kwargs)
