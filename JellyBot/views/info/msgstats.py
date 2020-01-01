from concurrent.futures.thread import ThreadPoolExecutor

from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.timezone import get_current_timezone

from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.utils import get_root_oid, get_channel_data
from extutils import safe_cast
from flags import WebsiteError
from mongodb.factory import MessageRecordStatisticsManager
from mongodb.helper import MessageStatsDataProcessor

KEY_MSG_INTV_FLOW = "msg_intvflow_data"
KEY_MSG_DAILY = "msg_daily_data"
KEY_MSG_DAILY_USER = "msg_daily_user"
KEY_MSG_USER_CHANNEL = "channel_user_msg"


def _msg_intv_flow_(channel_oid, hours_within, tzinfo):
    return KEY_MSG_INTV_FLOW, MessageRecordStatisticsManager.hourly_interval_message_count(
        channel_oid, hours_within, tzinfo)


def _msg_daily_(channel_oid, hours_within, tzinfo):
    return KEY_MSG_DAILY, MessageRecordStatisticsManager.daily_message_count(
        channel_oid, hours_within, tzinfo)


def _msg_user_daily_(channel_data, hours_within, tzinfo):
    return KEY_MSG_DAILY_USER, MessageStatsDataProcessor.get_user_daily_message(channel_data, hours_within, tzinfo)


def _channel_user_msg_(channel_data, hours_within):
    return KEY_MSG_USER_CHANNEL, MessageStatsDataProcessor.get_user_channel_messages(channel_data, hours_within)


def get_msg_stats_data_package(channel_data, hours_within, tzinfo):
    ret = {}

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="MsgStats") as executor:
        futures = [executor.submit(_msg_intv_flow_, channel_data.id, hours_within, tzinfo),
                   executor.submit(_msg_daily_, channel_data.id, hours_within, tzinfo),
                   executor.submit(_msg_user_daily_, channel_data, hours_within, tzinfo),
                   executor.submit(_channel_user_msg_, channel_data, hours_within)]

        # Non-lock call & Free resources when execution is done
        executor.shutdown(False)

        for completed in futures:
            key, result = completed.result()

            ret[key] = result

    return ret


class ChannelMessageStatsView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, DuplicatedCode
    def get(self, request, *args, **kwargs):
        channel_data = get_channel_data(kwargs)

        if not channel_data.ok:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_NOT_FOUND, {"channel_oid": channel_data.oid_org}, nav_param=kwargs)

        hours_within = safe_cast(request.GET.get("hours_within"), int)

        # channel_members = ProfileManager.get_channel_members(channel_oid)  # Reserved for per member analysis

        channel_name = channel_data.model.get_channel_name(get_root_oid(request))

        pkg = get_msg_stats_data_package(channel_data.model, hours_within, get_current_timezone())

        hours_within = hours_within or pkg[KEY_MSG_INTV_FLOW].hr_range
        msg_count = pkg[KEY_MSG_USER_CHANNEL].msg_count

        ctxt = {
            "channel_name": channel_name,
            "channel_data": channel_data.model,
            "hr_range": hours_within,
            "message_frequency": (hours_within * 3600) / msg_count if msg_count > 0 else 0
        }
        ctxt.update(pkg)

        return render_template(
            self.request, _("Channel Message Stats - {}").format(channel_name),
            "info/msgstats/main.html", ctxt, nav_param=kwargs)
