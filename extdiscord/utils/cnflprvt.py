"""
Bot confliction preventer.

Because that ther are multiple bots used for this project, one of it is for the service, one of them is for testing,
if there are some tests is running, the fact that service bot will also process the message being sent is undesirable,
hence this preventer.

This preventer will be automatically activated by importing this in the code.
To disable, delete the usage in ``log_bot_presence`` and ``prioritized_bot_exists`` in ``extdiscord.core``.

Configure ``id_to_check`` to decide which bot to process the message.
"""
from typing import Optional

from discord import Guild, Status

from extutils.logger import SYSTEM

__all__ = ("BotConflictionPreventer",)

SYSTEM.logger.info("Discord Bot Conflict Preventer is active.\n"
                   "Disable this by deleting the usage of `log_bot_presence` and `prioritized_bot_exists` "
                   "in `extdiscord.core` if you don't have 1+ Discord bot.")

LOCAL_BOT_ID = 623262302510252032
STABLE_BOT_ID = 621537611026137118


class BotConflictionPreventer:
    """Class to prevent message handling confliction/duplication."""

    id_list_checked = False
    id_to_check = [LOCAL_BOT_ID, STABLE_BOT_ID]
    """
    Discord bot client IDs.

    Order **matters** because this preventer will check the status of the bot sequentially.

    If any bot listed before the current bot, the handling process will be early terminated.
    """

    @classmethod
    def prioritized_bot_exists(cls, dc_guild: Optional[Guild]) -> bool:
        """
        Check if any bot having a higher priority exists.

        :param dc_guild: guild to check the status of the bots
        :return: if any prioritized bot exists
        """
        if not cls.id_list_checked:
            SYSTEM.logger.warning(
                "Discord Bot Conflict Preventer not initialized. Did you execute `initialize()` once?")
            return False

        if dc_guild is not None:
            for id_ in cls.id_to_check:
                bot = dc_guild.get_member(id_)
                if bot and bot.status == Status.online:
                    return True

        return False

    @classmethod
    def initialize(cls, id_: int):
        """
        Initialize the preventer.

        Check if the user with ID ``id_`` exists in the id checking list (``id_to_check``).
        Emits a warning in the log if not exists. **DOES NOT** terminate the program.

        :param id_: ID to be checked if  it is in the ID list
        """
        try:
            # Truncate the list to not to perform status check on the bot which have a lower priority
            cls.id_to_check = cls.id_to_check[:cls.id_to_check.index(id_)]
        except ValueError:
            SYSTEM.logger.warning("ID <%s> is not in the bot ID list.", id_)

        cls.id_list_checked = True
