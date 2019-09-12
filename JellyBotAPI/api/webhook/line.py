# DRAFT: Ping every time for user statistics
# DRAFT: Ping every time for auto reply
from django.views import View

from JellyBotAPI.components.mixin import CsrfExemptMixin
from JellyBotAPI.views import simple_str_response
from webhook.line import line_handle_event


class WebhookLineView(CsrfExemptMixin, View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.body.decode("utf-8")
        print("LINE Webhook request body:")
        print("\t" + str(body).replace("\n", "").replace(" ", ""))

        # handle webhook body
        line_handle_event(body, signature)

        return simple_str_response(request, "OK")
