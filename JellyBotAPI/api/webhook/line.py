# DRAFT: Ping every time for user statistics
# DRAFT: Ping every time for auto reply

from django.views import View

from webhook.line import line_handle_event


class WebhookLineView(View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.get_data(as_text=True)
        print("LINE Webhook request body:")
        print("\t" + body)

        # handle webhook body
        line_handle_event(body, signature)

        return "OK"
