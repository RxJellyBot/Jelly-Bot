# DRAFT: Ping every time for user statistics
# DRAFT: Ping every time for auto reply
import json

from django.views import View

from JellyBotAPI.components.mixin import CsrfExemptMixin
from webhook.line import line_handle_event


class WebhookLineView(CsrfExemptMixin, View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.body.decode("utf-8")
        print("LINE Webhook request body:")
        print("\t" + str(body))

        # handle webhook body
        line_handle_event(body, signature)

        return "OK"
