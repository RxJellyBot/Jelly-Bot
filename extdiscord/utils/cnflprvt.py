from typing import Optional

from discord import Guild, Status

__all__ = ["record_current_id", "prioritized_bot_exists"]

print("Discord Bot Conflict Preventer is active. "
      "Disable this by deleting the usage of `log_bot_presence` and `prioritized_bot_exists` in `extdiscord.core` "
      "if you forked the code repository.")


CURRENT_BOT_ID = -1
LOCAL_BOT_ID = 623262302510252032
BETA_BOT_ID = 621537611026137118
STABLE_BOT_ID = 621539717841944587

ids_to_check = [LOCAL_BOT_ID, BETA_BOT_ID, STABLE_BOT_ID]


def prioritized_bot_exists(dc_guild: Optional[Guild]):
    if CURRENT_BOT_ID == -1:
        print("Discord Bot Conflict Preventer not initialized. Did you execute `record_current_id` once?")
        return False

    if dc_guild is not None:
        for id_ in get_id_list_to_check():
            bot = dc_guild.get_member(id_)
            if bot and bot.status == Status.online:
                return True

    return False


def get_id_list_to_check():
    return [id_ for id_ in ids_to_check if id_ != CURRENT_BOT_ID]


def record_current_id(id_: int):
    global CURRENT_BOT_ID
    CURRENT_BOT_ID = id_
