from typing import Optional

from discord import Guild, Status

from extutils.logger import SYSTEM

__all__ = ["initialize", "prioritized_bot_exists"]

SYSTEM.logger.info("Discord Bot Conflict Preventer is active.\n"
                   "Disable this by deleting the usage of `log_bot_presence` and `prioritized_bot_exists` "
                   "in `extdiscord.core` if you don't have 1+ Discord bot.")

LOCAL_BOT_ID = 623262302510252032
STABLE_BOT_ID = 621537611026137118

id_list_checked = False

id_to_check = [LOCAL_BOT_ID, STABLE_BOT_ID]


def prioritized_bot_exists(dc_guild: Optional[Guild]):
    if not id_list_checked:
        SYSTEM.logger.warning("Discord Bot Conflict Preventer not initialized. Did you execute `initialize()` once?")
        return False

    if dc_guild is not None:
        for id_ in id_to_check:
            bot = dc_guild.get_member(id_)
            if bot and bot.status == Status.online:
                return True

    return False


def initialize(id_: int):
    global id_to_check, id_list_checked

    try:
        id_to_check = id_to_check[:id_to_check.index(id_)]
    except ValueError:
        SYSTEM.logger.warning(f"ID {id_} is not in the bot ID list.")

    id_list_checked = True
