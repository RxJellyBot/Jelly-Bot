# DRAFT: Ping every time for user statistics
from django.views import View

from JellyBotAPI.components.mixin import CsrfExemptMixin
from JellyBotAPI.views import simple_str_response
from external.line import line_handle_event
from external.line.logger import LINE


class WebhookLineView(CsrfExemptMixin, View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.body.decode("utf-8")
        LINE.logger.info("LINE Webhook request body: " + "\t" + str(body).replace("\n", "").replace(" ", ""))

        # handle external body
        line_handle_event(body, signature)

        return simple_str_response(request, "OK")
