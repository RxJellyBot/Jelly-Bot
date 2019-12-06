from datetime import datetime, timezone
from typing import List, Tuple, Type
import traceback

from discord import Embed
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from linebot.models import TextSendMessage, ImageSendMessage

from flags import MessageType
from extutils.utils import list_insert_in_between
from extutils.emailutils import MailSender
from extutils.line_sticker import LineStickerManager
from JellyBot.systemconfig import PlatformConfig, HostUrl
from mongodb.factory import ExtraContentManager

from .pipe_out import HandledMessageCalculateResult, HandledMessageEventsHolder, HandledMessageEvent, \
    HandledMessageEventText


class ToSiteReason:
    TOO_LONG = _("Message length overlimit.")
    TOO_MANY_RESPONSES = _("Responses length overlimit.")
    TOO_MANY_LINES = _("Too many lines.")
    LATEX_AVAILABLE = _("LaTeX available.")
    FORCED_ONSITE = _("Content was forced to be displayed on the website.")


class HandledEventsHolderPlatform:
    def __init__(self, holder: HandledMessageEventsHolder, config_class: Type[PlatformConfig]):
        self.config_class = config_class
        self.to_send: List[Tuple[MessageType, str]] = []
        self.to_site: List[Tuple[str, str]] = []

        self._sort_data_(holder, config_class)

        if len(self.to_send) > config_class.max_responses:
            self.to_site.append((ToSiteReason.TOO_MANY_RESPONSES, self.to_send.pop(config_class.max_responses - 1)[1]))

        if len(self.to_site) > 0:
            rec_result = ExtraContentManager.record_extra_message(
                self.to_site, datetime.now(tz=timezone.utc).strftime("%m-%d %H:%M:%S UTC%z"))

            if rec_result.success:
                url = f'{HostUrl}{reverse("page.extra", kwargs={"page_id": str(rec_result.model_id)})}'

                self.to_send.append(
                    (MessageType.TEXT,
                     _("{} content(s) was recorded to the database because of the following reason(s):{}\nURL: {}")
                     .format(
                         len(self.to_site),
                         "".join([f"\n - {reason}" for reason, content in self.to_site]),
                         url)
                     )
                )
            else:
                MailSender.send_email_async(
                    f"Failed to record extra content.<hr>Result: {rec_result.outcome}<hr>"
                    f"To Send:<br>{str(self.to_send)}<br>To Site:<br>{str(self.to_site)}<hr>"
                    f"Exception:<br><pre>"
                    f"{traceback.format_exception(None, rec_result.exception, rec_result.exception.__traceback__)}"
                    f"</pre>",
                    subject="Failure on Recording Extra Content")
                self.to_send.append(
                    _("Content(s) is supposed to be recorded to database but failed. "
                      "An error report should be sent for investigation."))

    def _sort_data_(self, holder: HandledMessageEventsHolder, config_class: Type[PlatformConfig]):
        e: HandledMessageEvent
        for e in holder:
            if len(e.content) > config_class.max_content_length:
                self.to_site.append((ToSiteReason.TOO_LONG, e.content))
                continue
            elif len(self.to_send) > config_class.max_responses:
                self.to_site.append((ToSiteReason.TOO_MANY_RESPONSES, e.content))
                continue

            if isinstance(e, HandledMessageEventText):
                if e.force_extra:
                    self.to_site.append((ToSiteReason.FORCED_ONSITE, e.content))
                    continue
                elif not e.bypass_multiline_check and len(self.to_send) > config_class.max_content_lines:
                    # TEST: Test if bypass multiline check is working. Setup an auto-reply with 20+ Line and trigger it.
                    #   Content should be displayed directly if working properly.
                    self.to_site.append((ToSiteReason.TOO_MANY_LINES, e.content))
                    continue

            if isinstance(e, HandledMessageCalculateResult):
                if e.latex_available:
                    self.to_send.append((e.msg_type, e.content))
                    self.to_site.append((ToSiteReason.LATEX_AVAILABLE, e.latex_for_html))
                    continue

            self.to_send.append((e.msg_type, e.content))

    def send_line(self, reply_token):
        if self.to_send:
            from extline import LineApiWrapper

            send_list = []

            for msg_type, content in self.to_send:
                if msg_type == MessageType.TEXT:
                    send_list.append(TextSendMessage(text=content))
                elif msg_type == MessageType.IMAGE:
                    send_list.append(ImageSendMessage(original_content_url=content, preview_image_url=content))
                elif msg_type == MessageType.LINE_STICKER:
                    sticker_url = LineStickerManager.get_sticker_url(content)
                    send_list.append(ImageSendMessage(original_content_url=sticker_url, preview_image_url=sticker_url))

            LineApiWrapper.reply_message(reply_token, send_list)

    async def send_discord(self, dc_channel):
        send_list = []

        for msg_type, content in self.to_send:
            if msg_type == MessageType.TEXT:
                send_list.append(content)
            elif msg_type == MessageType.IMAGE:
                send_list.append(
                    Embed()
                    .set_image(url=content)
                    .set_footer(text=_("Image URL: {}").format(content)))
            elif msg_type == MessageType.LINE_STICKER:
                send_list.append(
                    Embed()
                    .set_image(url=LineStickerManager.get_sticker_url(content))
                    .set_footer(text=_("Sticker ID: {}").format(content)))

        # Insert separator between responses
        send_list = list_insert_in_between(send_list, "------------------------------")

        # 2 For loops so that responses seem to be sent at once
        for s in send_list:
            if isinstance(s, Embed):
                await dc_channel.send(embed=s)
            else:
                await dc_channel.send(s)
