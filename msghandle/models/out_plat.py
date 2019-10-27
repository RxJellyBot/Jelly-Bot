from datetime import datetime, timezone
from typing import List, Tuple, Type
import traceback

from django.urls import reverse

from extutils.emailutils import MailSender
from JellyBot.systemconfig import PlatformConfig, HostUrl
from mongodb.factory import ExtraContentManager
from msghandle.translation import gettext as _

from .pipe_out import HandledMessageCalculateResult, HandledMessageEventsHolder


class ToSiteReason:
    TOO_LONG = _("Message length overlimit.")
    TOO_MANY_RESPONSES = _("Responses length overlimit.")
    TOO_MANY_LINES = _("Too many lines.")
    LATEX_AVAILABLE = _("LaTeX available.")


class HandledEventsHolderPlatform:
    def __init__(self, holder: HandledMessageEventsHolder, config_class: Type[PlatformConfig]):
        self.config_class = config_class
        self.to_send: List[str] = []
        self.to_site: List[Tuple[str, str]] = []

        self._sort_data_(holder, config_class)

        if len(self.to_send) > config_class.max_responses:
            self.to_site.append((ToSiteReason.TOO_MANY_RESPONSES, self.to_send.pop(config_class.max_responses - 1)))

        if len(self.to_site) > 0:
            rec_result = ExtraContentManager.record_extra_message(
                self.to_site, datetime.now(tz=timezone.utc).strftime("%m-%d %H:%M:%S UTC%z"))

            if rec_result.success:
                url = f'{HostUrl}{reverse("page.extra", kwargs={"page_id": str(rec_result.model_id)})}'

                self.to_send.append(
                    _("{} content(s) was recorded to the database "
                      "because of the following reason(s):{}\nURL: {}")
                    .format(
                        len(self.to_site),
                        "".join([f"\n - {getattr(ToSiteReason, v)}" for v in vars(ToSiteReason)
                                 if not callable(getattr(ToSiteReason, v)) and not v.startswith("__")]),
                        url))
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
        for e in holder:
            if len(e.content) > config_class.max_content_length:
                self.to_site.append((ToSiteReason.TOO_LONG, e.content))
            elif len(self.to_send) > config_class.max_responses:
                self.to_site.append((ToSiteReason.TOO_MANY_RESPONSES, e.content))
            elif not e.bypass_multiline_check and len(self.to_send) > config_class.max_content_lines:
                # TEST: Test if bypass multiline check is working. Setup an auto-reply with 20+ Line and trigger it.
                #   Content should be displayed directly if working properly.
                self.to_site.append((ToSiteReason.TOO_MANY_LINES, e.content))
            elif isinstance(e, HandledMessageCalculateResult) and e.latex_available:
                self.to_site.append((ToSiteReason.LATEX_AVAILABLE, e.latex_for_html))
            else:
                self.to_send.append(e.content)
