"""
Functions related to the main event handling.
"""
import traceback

from extutils.emailutils import MailSender
from msghandle import handle_message_main
from msghandle.models import (
    Event, TextMessageEventObject, ImageMessageEventObject,
    HandledMessageEventsHolder
)

from .logger import DISCORD

__all__ = ["handle_discord_main", "handle_error"]


def handle_discord_main(event: Event) -> HandledMessageEventsHolder:
    """Main function to handle the message received from the discord bot."""
    try:
        # Early return on not-handled object
        if not isinstance(event, (TextMessageEventObject, ImageMessageEventObject)):
            DISCORD.logger.info("Discord event object not handled. "
                                "Raw: %s" % event.raw if hasattr(event, "raw") else event)
            return HandledMessageEventsHolder(event.channel_model)

        return handle_message_main(event)
    except Exception as ex:  # pylint: disable=W0703
        handle_error(ex)
        return HandledMessageEventsHolder(event.channel_model)


def handle_error(ex: Exception):
    """Function to be called when any error occurred during the discord message handling."""
    subject = "Error on Discord Message Processing"

    html = f"<h4>{ex}</h4>\n" \
           f"<hr>\n" \
           f"<pre>Traceback:\n" \
           f"{traceback.format_exc()}</pre>\n"
    MailSender.send_email_async(html, subject=subject)

    DISCORD.logger.error(subject, exc_info=True)
