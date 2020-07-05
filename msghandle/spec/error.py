import traceback
from typing import List

from linebot.exceptions import LineBotApiError

from extutils.emailutils import MailSender
from extline.handler.error import handle_error as handle_line_error
from extdiscord.handle import handle_error as handle_discord_error
from flags import Platform
from msghandle.models import MessageEventObject, HandledMessageEvent, HandledMessageEventText
from strres.msghandle import HandledResult


def handle_error_main(e: MessageEventObject, ex: Exception) -> List[HandledMessageEvent]:
    if e.platform == Platform.LINE:
        handle_line_error(ex, "Error handling LINE message", e.raw, e.user_model.id)
    elif e.platform == Platform.DISCORD:
        handle_discord_error(ex)
    else:
        html = f"<h4>{e}</h4>\n" \
               f"<hr>\n" \
               f"<pre>Traceback:\n" \
               f"{traceback.format_exc()}</pre>\n"
        MailSender.send_email_async(html, subject=f"Error on Message Processing ({e.platform})")

    if not isinstance(ex, LineBotApiError) or not ex.status_code == 500:
        return [HandledMessageEventText(content=HandledResult.ErrorHandle)]
