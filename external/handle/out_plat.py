from collections import OrderedDict
from typing import List, Tuple, Type
import traceback
from gettext import gettext as _

from django.urls import reverse

from extutils.emailutils import MailSender
from JellyBot.sysconfig import PlatformConfig
from flags import ExtraContentType
from mongodb.factory import ExtraContentManager


class ToSiteReason:
    TOO_LONG = _("Message length overlimit.")
    TOO_MANY_RESPONSES = _("Responses length overlimit.")


class HandledEventsHolderPlatform:
    def __init__(self, holder, request, config_class: Type[PlatformConfig]):
        self.request = request
        self.config_class = config_class
        self.to_send: List[str] = []
        self.to_site: OrderedDict[int, Tuple[str, str]] = OrderedDict()

        for idx, e in enumerate(holder, start=1):
            if len(e.content) > config_class.max_content_length:
                self.to_site[idx] = (ToSiteReason.TOO_LONG, e.content)
            elif len(self.to_send) > config_class.max_responses:
                self.to_site[idx] = (ToSiteReason.TOO_MANY_RESPONSES, e.content)
            else:
                self.to_send.append(e.content)

        if len(self.to_send) > config_class.max_responses:
            self.to_site[config_class.max_responses] = \
                (ToSiteReason.TOO_MANY_RESPONSES, self.to_send.pop(config_class.max_responses - 1))

    def push_content(self):
        if len(self.to_site) > 0:
            tab_list: List[str] = []
            tab_content: List[str] = []
            msg_prefix = _("Message ")

            for idx, data in self.to_site.items():
                reason, content = data
                common_key = f"msg-{idx}"

                tab_list.append(
                    f'<a class="list-group-item list-group-item-action" '
                    f'id="list-{common_key}" '
                    f'data-toggle="list" href="#{common_key}" role="tab">{msg_prefix}{idx}</a>')
                tab_content.append(
                    f'<div class="tab-pane fade" id="{common_key}" role="tabpanel" '
                    f'aria-labelledby="list-{common_key}"><h4>{reason}</h4>{content}</div>')

            rec_result = ExtraContentManager.record_content(
                ExtraContentType.PURE_TEXT,
                f'<div class="row">'
                f'<div class="col-4"><div class="list-group" id="list-tab" role="tablist">{"".join(tab_list)}</div>'
                f'</div>'
                f'<div class="col-8"><div class="tab-content" id="nav-tabContent">{"".join(tab_content)}</div>'
                f'</div>'
                f'</div>')

            if rec_result.success:
                url = self.request.build_absolute_uri(
                    reverse("page.extra", kwargs={"page_id": str(rec_result.model_id)}))

                self.to_send.append(
                    _("Content(s) was recorded to the database because either the length is too long (over {}) or "
                      "the limit of count of responses has reached (max {}).\n{}").format(
                        self.config_class.max_content_length, self.config_class.max_responses, url))
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
