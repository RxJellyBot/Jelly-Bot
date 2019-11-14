from django.urls import reverse

from flags import BotFeature
from mongodb.helper import MessageStatsDataProcessor
from msghandle.models import TextMessageEventObject
from msghandle.translation import gettext as _
from JellyBot.systemconfig import HostUrl

from ._base_ import CommandNode

cmd = CommandNode(
    ["info", "id"], 500, _("Information"),
    _("Check the information of various things (see the description section for more details)."))
cmd_me = cmd.new_child_node(["me", "my"])
cmd_ch = cmd.new_child_node(["ch", "channel"])
cmd_id = cmd.new_child_node(["id"])


def _user_id_section_(e: TextMessageEventObject):
    ret = [_("User ID: `{}`").format(e.user_model.id)]

    if e.user_token:
        ret.append(_("User Token: `{}`").format(e.user_token))

    return ret


def _channel_id_section_(e: TextMessageEventObject):
    return [_("Channel ID: `{}`").format(e.channel_model.id),
            _("Channel Token: `{}`").format(e.channel_model.token)]


def _channel_info_url_(e: TextMessageEventObject):
    return [_("Channel Detailed Info URL: {}{}").format(
        HostUrl, reverse("info.channel", kwargs={"channel_oid": e.channel_oid}))]


def _chcoll_id_section_(e: TextMessageEventObject):
    ret = []

    if e.chcoll_model:
        ret.append(_("Channel Collection ID: `{}`").format(e.chcoll_model.id))
        ret.append(_("Channel Collection Token: `{}`").format(e.chcoll_model.token))

    return ret


def _chcoll_info_url_(e: TextMessageEventObject):
    if e.chcoll_model:
        return [_("Channel Collection Detailed Info URL: {}{}").format(
            HostUrl, reverse("info.chcoll", kwargs={"chcoll_oid": e.chcoll_model.id}))]
    return []


def _user_ranking_section_(e: TextMessageEventObject):
    ret = []

    rk_ch_1d = MessageStatsDataProcessor.get_user_channel_ranking(e.channel_model, e.user_model.id, 24)
    if rk_ch_1d.available:
        ret.append(_("Current Channel Message Count Ranking in 1 Day - {}").format(str(rk_ch_1d)))

    rk_ch_7d = MessageStatsDataProcessor.get_user_channel_ranking(e.channel_model, e.user_model.id, 168)
    if rk_ch_7d.available:
        ret.append(_("Current Channel Message Count Ranking in 7 Days - {}").format(str(rk_ch_7d)))

    if e.chcoll_model:
        rk_ccoll_1d = MessageStatsDataProcessor.get_user_chcoll_ranking(e.chcoll_model, e.user_model.id, 24)
        if rk_ccoll_1d.available:
            ret.append(_("Channel Collection Message Count Ranking in 1 Day - {}").format(str(rk_ccoll_1d)))

        rk_ccoll_7d = MessageStatsDataProcessor.get_user_chcoll_ranking(e.chcoll_model, e.user_model.id, 168)
        if rk_ccoll_7d.available:
            ret.append(_("Channel Collection Message Count Ranking in 7 Days - {}").format(str(rk_ccoll_7d)))

    return ret


def _channel_msg_count_list_section_(e: TextMessageEventObject, limit):
    ret = []

    mem_stats = list(
        sorted(
            MessageStatsDataProcessor.get_user_channel_messages(
                e.channel_model, hours_within=168).member_stats,
            key=lambda x: x.message_count, reverse=True))[:limit]

    ret.append(_("Top {} Message Count in 7 Days in this channel:").format(limit))
    ret.append("```")
    ret.append("\n".join(
        [f"{entry.message_count:>6} ({entry.message_percentage:>7.02%}) - {entry.user_name}" for entry in mem_stats]))
    ret.append("```")

    return ret


def _chcoll_msg_count_list_section_(e: TextMessageEventObject, limit):
    ret = []

    if e.chcoll_model:
        mem_stats_chcoll = list(
            sorted(
                MessageStatsDataProcessor.get_user_chcoll_messages(
                    e.chcoll_model, hours_within=168).member_stats,
                key=lambda x: x.message_count, reverse=True))[:limit]

        ret.append("")
        ret.append(_("Top {} Message Count in 7 Days in this channel collection:").format(limit))
        ret.append("```")
        ret.append("\n".join(
            [f"{entry.message_count:>6} ({entry.message_percentage:>7.02%}) - {entry.user_name}" for entry in
             mem_stats_chcoll]))
        ret.append("```")

    return ret


@cmd_id.command_function(feature_flag=BotFeature.TXT_INFO_ID)
def check_ids(e: TextMessageEventObject):
    ret = []

    ret.extend(_chcoll_id_section_(e))
    ret.extend(_channel_id_section_(e))
    ret.extend(_user_id_section_(e))

    return "\n".join(ret)


@cmd_ch.command_function(feature_flag=BotFeature.TXT_INFO_CHANNEL)
def check_channel_info(e: TextMessageEventObject):
    ret = []

    limit = 10

    ret.extend(_chcoll_id_section_(e))
    ret.extend(_chcoll_info_url_(e))
    ret.extend(_channel_id_section_(e))
    ret.extend(_channel_info_url_(e))

    ret.append("")
    ret.extend(_chcoll_msg_count_list_section_(e, limit))
    ret.extend(_channel_msg_count_list_section_(e, limit))

    return "\n".join(ret)


@cmd_me.command_function(feature_flag=BotFeature.TXT_INFO_USER)
def check_sender_identity(e: TextMessageEventObject):
    ret = []

    ret.extend(_user_id_section_(e))
    ret.extend(_user_ranking_section_(e))

    return "\n".join(ret)
