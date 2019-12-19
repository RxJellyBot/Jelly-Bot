from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional

from bson import ObjectId
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.timezone import get_current_timezone

from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.utils import get_root_oid
from extutils import safe_cast
from flags import WebsiteError
from models import ChannelModel
from mongodb.factory import ChannelManager, BotFeatureUsageDataManager
from mongodb.helper import BotUsageStatsDataProcessor

KEY_HR_FLOW = "usage_hr_data"
KEY_TOTAL_USAGE = "total_usage"
KEY_MEMBER_USAGE = "member_usage"


def _hr_flow_(channel_oid, hours_within, tzinfo):
    return KEY_HR_FLOW, BotFeatureUsageDataManager.get_channel_hourly_avg(
        channel_oid, hours_within, True, tzinfo)


def _total_usage_(channel_oid, hours_within):
    return KEY_TOTAL_USAGE, BotFeatureUsageDataManager.get_channel_usage(
        channel_oid, hours_within, False)


def _member_usage_(channel_oid, hours_within):
    return KEY_MEMBER_USAGE, BotUsageStatsDataProcessor.get_per_user_bot_usage(
        channel_oid, hours_within)


def get_bot_stats_data_package(channel_data, hours_within, tzinfo):
    ret = {}

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="BotStats") as executor:
        futures = [executor.submit(_hr_flow_, channel_data.id, hours_within, tzinfo),
                   executor.submit(_total_usage_, channel_data.id, hours_within),
                   executor.submit(_member_usage_, channel_data, hours_within)]

        # Non-lock call & Free resources when execution is done
        executor.shutdown(False)

        for completed in futures:
            key, result = completed.result()

            ret[key] = result

    return ret


class ChannelBotUsageStatsView(TemplateResponseMixin, View):
    # noinspection PyUnusedLocal, DuplicatedCode
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

        pkg = get_bot_stats_data_package(channel_data, hours_within, get_current_timezone())

        ctxt = {
            "ch_name": channel_data.get_channel_name(get_root_oid(request)),
            "channel_data": channel_data,
            "hr_range": hours_within or pkg[KEY_HR_FLOW].hr_range
        }
        ctxt.update(pkg)

        return render_template(
            self.request, _("Bot Usage Stats - {}").format(channel_oid),
            "info/botstats/main.html", ctxt, nav_param=kwargs)
