"""Webhook endpoint for LINE."""
from django.views import View

from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.views import simple_str_response
from extline import line_handle_event
from extline.logger import LINE


class WebhookLineView(CsrfExemptRelay, View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        """Handle LINE webhook requests."""

        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.body.decode("utf-8")
        LINE.logger.info("LINE Webhook request body: " + "\t" + str(body).replace("\n", "").replace(" ", ""))

        # handle external body
        line_handle_event(request, body, signature)

        return simple_str_response(request, "OK")
