import traceback

from extutils.emailutils import MailSender
from msghandle import handle_message_main
from msghandle.models import Event, TextMessageEventObject, HandledMessageEventsHolder

from .logger import DISCORD

__all__ = ["handle_discord_main"]

# Command Structure - https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html


def handle_discord_main(e: Event) -> HandledMessageEventsHolder:
    try:
        if isinstance(e, TextMessageEventObject):
            return handle_message_main(e)
        else:
            DISCORD.logger.info(f"Discord event object not handled. Raw: {e.raw}")
            return HandledMessageEventsHolder()
    except Exception as e:
        handle_error(e)
        return HandledMessageEventsHolder()


def handle_error(e: Exception):
    subject = "Error on Discord Message Processing"

    html = f"<h4>{e}</h4>\n" \
           f"<hr>\n" \
           f"<pre>Traceback:\n" \
           f"{traceback.format_exc()}</pre>\n"
    MailSender.send_email_async(html, subject=subject)

    DISCORD.logger.error(subject, exc_info=True)