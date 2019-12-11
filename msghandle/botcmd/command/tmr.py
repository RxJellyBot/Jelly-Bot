from dateutil import parser
from typing import List

from django.utils.translation import gettext_lazy as _

from extutils.boolext import str_to_bool, true_word, false_word, StrBoolResult
from extutils.dt import is_tz_naive
from flags import BotFeature, CommandScopeCollection
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from mongodb.factory import TimerManager
from JellyBot.systemconfig import Bot

from ._base_ import CommandNode


cmd = CommandNode(
    codes=["tmr", "t", "timer"], order_idx=1100, name=_("Timer"),
    brief_description=_("Commands related to timer."),
    description=_("Commands related to timer.\n\nFlag `countup` defaults to `False`.")
)
cmd_add = cmd.new_child_node(codes=["a", "aa", "add"])
cmd_list = cmd.new_child_node(codes=["l", "list", "lst"])


# ------------------------- Add -------------------------

add_kw_help = _("Keyword to get the timer. "
                "The bot will reply the timer status whenever the keyword has been detected in the designated channel.")
title_help = _("Title of the timer.")
datetime_help = _("String of the target datetime of the timer.\n\n"
                  "- Timezone will be the user's configurated timezone if not specified.\n\n"
                  "- General format should be accepted. If not, please visit "
                  "[this page.](https://dateutil.readthedocs.io/en/stable/parser.html)\n\n"
                  "- If the timer is set to not to keep counting after it reaches the target time, the timer will be "
                  "automatically permanently deleted after {} days.").format(Bot.Timer.AutoDeletionDays)
continue_help = _("A word that can indicate if the timer should keep counting up or not.\n\n"
                  "- Words that means POSITIVE: {}\n\n"
                  "- Words that means NEGATIVE: {}").format(" / ".join(true_word), " / ".join(false_word))


@cmd_add.command_function(
    feature_flag=BotFeature.TXT_TMR_ADD,
    arg_count=4,
    arg_help=[add_kw_help, title_help, datetime_help, continue_help],
    scope=CommandScopeCollection.GROUP_ONLY
)
def add_timer(e: TextMessageEventObject, keyword: str, title: str, dt: str, countup: str) \
        -> List[HandledMessageEventText]:
    # Parse datetime string
    try:
        dt = parser.parse(dt, ignoretz=False)
    except (ValueError, OverflowError):
        return [HandledMessageEventText(content=_("Failed to parse the string of datetime. (`{}`)").format(dt))]

    # Attach timezone if needed
    if is_tz_naive(dt):
        dt = dt.replace(tzinfo=e.user_model.config.tzinfo)

    # Check `countup` flag
    ctup = str_to_bool(countup)

    if ctup == StrBoolResult.UNKNOWN:
        return [
            HandledMessageEventText(content=_(
                "Unknown flag to indicate if the timer will countup once the time is up. (`{}`)").format(countup))]

    outcome = TimerManager.add_new_timer(e.channel_oid, keyword, title, dt, ctup.to_bool())

    if outcome.is_success:
        return [HandledMessageEventText(content=_("Timer added."))]
    else:
        return [HandledMessageEventText(content=_("Failed to add timer. Outcome code: `{}`").format(outcome))]


@cmd_add.command_function(
    feature_flag=BotFeature.TXT_TMR_ADD,
    arg_count=3,
    arg_help=[add_kw_help, title_help, datetime_help],
    scope=CommandScopeCollection.GROUP_ONLY
)
def add_timer_smpl(e: TextMessageEventObject, keyword: str, title: str, dt: str) \
        -> List[HandledMessageEventText]:
    return add_timer(e, keyword, title, dt, false_word[0])


@cmd_list.command_function(
    feature_flag=BotFeature.TXT_TMR_LIST_ALL,
    scope=CommandScopeCollection.GROUP_ONLY
)
def list_all_timer(e: TextMessageEventObject) \
        -> List[HandledMessageEventText]:
    tmrs = TimerManager.list_all_timer(e.channel_oid)

    if tmrs.has_data:
        return [HandledMessageEventText(content=_("All Timers in this Channel:\n") + tmrs.to_string(e.user_model))]
