from concurrent.futures.thread import ThreadPoolExecutor

from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.timezone import get_current_timezone

from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.utils import get_root_oid, get_channel_data
from extutils import safe_cast
from flags import WebsiteError
from mongodb.factory import BotFeatureUsageDataManager
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
        channel_data = get_channel_data(kwargs)

        if not channel_data.ok:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_NOT_FOUND, {"channel_oid": channel_data.oid_org}, nav_param=kwargs)

        hours_within = safe_cast(request.GET.get("hours_within"), int)

        # channel_members = ProfileManager.get_channel_members(channel_oid)  # Reserved for per member analysis

        pkg = get_bot_stats_data_package(channel_data.model, hours_within, get_current_timezone())

        ctxt = {
            "channel_name": channel_data.model.get_channel_name(get_root_oid(request)),
            "channel_data": channel_data.model,
            "hr_range": hours_within or pkg[KEY_HR_FLOW].hr_range
        }
        ctxt.update(pkg)

        return render_template(
            self.request, _("Bot Usage Stats - {}").format(channel_data.model.id),
            "info/botstats/main.html", ctxt, nav_param=kwargs)
