import traceback

from extutils.emailutils import MailSender
from external.handle import EventObject, TextEventObject, handle_main, HandledEventsHolder

from .logger import DISCORD

__all__ = ["handle_discord_main"]


def handle_discord_main(e: EventObject) -> HandledEventsHolder:
    try:
        if isinstance(e, TextEventObject):
            return handle_main(e)
        else:
            DISCORD.logger.info(f"Discord event object not handled. Raw: {e.raw}")
            return HandledEventsHolder()
    except Exception as e:
        handle_error(e)
        return HandledEventsHolder()


def handle_error(e: Exception):
    subject = "Error on Discord Message Processing"

    html = f"<h4>{e}</h4>\n" \
           f"<hr>\n" \
           f"<pre>Traceback:\n" \
           f"{traceback.format_exc()}</pre>\n"
    MailSender.send_email_async(html, subject=subject)

    DISCORD.logger.error(subject, exc_info=True)
