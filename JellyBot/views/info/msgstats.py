from concurrent.futures.thread import ThreadPoolExecutor

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.timezone import get_current_timezone

from JellyBot.views import render_template
from JellyBot.utils import get_root_oid
from JellyBot.components.mixin import ChannelOidRequiredMixin
from JellyBot.systemconfig import Website
from extutils import safe_cast, dt_to_objectid
from extutils.dt import parse_to_dt
from mongodb.factory import MessageRecordStatisticsManager
from mongodb.helper import MessageStatsDataProcessor

KEY_MSG_INTV_FLOW = "msg_intvflow_data"
KEY_MSG_INTV_COUNT = "msg_intvcount_data"
KEY_MSG_DAILY = "msg_daily_data"
KEY_MSG_MEAN = "msg_mean_data"
KEY_MSG_DAILY_USER = "msg_daily_user"
KEY_MSG_USER_CHANNEL = "channel_user_msg"


def _msg_intv_flow_(channel_oid, tzinfo, *, hours_within=None, start=None, end=None):
    return KEY_MSG_INTV_FLOW, MessageRecordStatisticsManager.hourly_interval_message_count(
        channel_oid, tzinfo_=tzinfo, hours_within=hours_within, start=start, end=end)


def _msg_intv_count_(
        channel_data, tzinfo, available_only, *, hours_within=None, start=None, end=None, period_count=None):
    return KEY_MSG_INTV_COUNT, MessageStatsDataProcessor.get_user_channel_message_count_interval(
        channel_data, hours_within=hours_within, start=start, end=end,
        period_count=period_count, tz=tzinfo, available_only=available_only)


def _msg_daily_(channel_oid, tzinfo, *, hours_within=None, start=None, end=None):
    return KEY_MSG_DAILY, MessageRecordStatisticsManager.daily_message_count(
        channel_oid, tzinfo_=tzinfo, hours_within=hours_within, start=start, end=end)


def _msg_mean_(channel_oid, tzinfo, *, hours_within=None, start=None, end=None):
    return KEY_MSG_MEAN, MessageRecordStatisticsManager.mean_message_count(
        channel_oid, tzinfo_=tzinfo, hours_within=hours_within, start=start, end=end, max_mean_days=14)


def _msg_user_daily_(channel_data, tzinfo, available_only, *, hours_within=None, start=None, end=None):
    return KEY_MSG_DAILY_USER, MessageStatsDataProcessor.get_user_daily_message(
        channel_data, tz=tzinfo, hours_within=hours_within, start=start, end=end, available_only=available_only)


def _channel_user_msg_(channel_data, available_only, *, hours_within=None, start=None, end=None):
    return KEY_MSG_USER_CHANNEL, MessageStatsDataProcessor.get_user_channel_messages(
        channel_data, hours_within=hours_within, start=start, end=end, available_only=available_only)


def get_msg_stats_data_package(
        channel_data, tzinfo, incl_unav, *, hours_within=None, start=None, end=None, period_count=None):
    ret = {}

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="MsgStats") as executor:
        available_only = not incl_unav

        futures = [executor.submit(_msg_intv_flow_, channel_data.id, tzinfo,
                                   hours_within=hours_within, start=start, end=end),
                   executor.submit(_msg_intv_count_, channel_data, tzinfo, available_only,
                                   hours_within=hours_within, start=start, end=end, period_count=period_count),
                   executor.submit(_msg_daily_, channel_data.id, tzinfo,
                                   hours_within=hours_within, start=start, end=end),
                   executor.submit(_msg_mean_, channel_data.id, tzinfo,
                                   hours_within=hours_within, start=start, end=end),
                   executor.submit(_msg_user_daily_, channel_data, tzinfo, available_only,
                                   hours_within=hours_within, start=start, end=end),
                   executor.submit(_channel_user_msg_, channel_data, available_only,
                                   hours_within=hours_within, start=start, end=end)]

        # Non-lock call & Free resources when execution is done
        executor.shutdown(False)

        for completed in futures:
            key, result = completed.result()

            ret[key] = result

    return ret


class ChannelMessageStatsView(ChannelOidRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, DuplicatedCode
    def get(self, request, *args, **kwargs):
        channel_data = self.get_channel_data(*args, **kwargs)

        hours_within = safe_cast(request.GET.get("hours_within"), int)
        incl_unav = safe_cast(request.GET.get("incl_unav"), bool)
        period_count = safe_cast(request.GET.get("period"), int) or Website.Message.DefaultPeriodCount
        if period_count <= 0:
            messages.warning(request, _("Period count cannot be less than or equal to 0."))
            period_count = Website.Message.DefaultPeriodCount

        # Get starting timestamp
        dt_start_str = request.GET.get("start")
        dt_start = None
        if dt_start_str:
            dt_start = parse_to_dt(dt_start_str, tzinfo_=get_current_timezone())
            if not dt_start:
                messages.warning(
                    request, _("Failed to parse the starting timestamp. Received: {}").format(dt_start_str))
            elif not dt_to_objectid(dt_start):
                dt_start = None
                messages.warning(request, _("Start time out of range."))

        # Get ending timestamp
        dt_end_str = request.GET.get("end")
        dt_end = None
        if dt_end_str:
            dt_end = parse_to_dt(dt_end_str, tzinfo_=get_current_timezone())
            if not dt_end:
                messages.warning(
                    request, _("Failed to parse the ending timestamp. Received: {}").format(dt_end_str))
            elif not dt_to_objectid(dt_end):
                dt_end = None
                messages.warning(request, _("End time out of range."))

        # Check starting and ending timestamp
        if dt_start and dt_end and dt_start > dt_end:
            dt_start = None
            dt_end = None
            messages.warning(
                request, _("Invalid timestamp: Ending time is before the starting time."))

        channel_name = channel_data.model.get_channel_name(get_root_oid(request))

        pkg = get_msg_stats_data_package(
            channel_data.model, get_current_timezone(), incl_unav,
            hours_within=hours_within, start=dt_start, end=dt_end, period_count=period_count)

        hours_within = pkg[KEY_MSG_INTV_FLOW].hr_range or hours_within
        msg_count = pkg[KEY_MSG_USER_CHANNEL].msg_count

        ctxt = {
            "channel_name": channel_name,
            "channel_data": channel_data.model,
            "hr_range": hours_within,
            "dt_start": dt_start.replace(tzinfo=None).isoformat() if dt_start else "",
            "dt_end": dt_end.replace(tzinfo=None).isoformat() if dt_end else "",
            "message_frequency": (hours_within * 3600) / msg_count if msg_count > 0 else 0,
            "incl_unav": incl_unav,
            "period_count": period_count
        }
        ctxt.update(pkg)

        return render_template(
            self.request, _("Channel Message Stats - {}").format(channel_name),
            "info/msgstats/main.html", ctxt, nav_param=kwargs)
