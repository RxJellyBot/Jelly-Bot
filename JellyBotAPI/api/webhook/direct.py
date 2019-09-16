from django.views import View
from django.utils.translation import gettext_lazy as _

from JellyBotAPI.components.mixin import CsrfExemptMixin
from JellyBotAPI.api.static import param
from JellyBotAPI.views import simple_str_response
from external.handle import EventObjectFactory, handle_main


class DirectMessageWebhookView(CsrfExemptMixin, View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get(self, request, *args, **kwargs):
        msg = request.GET.get(param.Message.MESSAGE)
        if msg:
            return handle_main(EventObjectFactory.from_direct(msg))
        else:
            return simple_str_response(request, _(f"Provide {param.Message.MESSAGE} as a query parameter for message."))
