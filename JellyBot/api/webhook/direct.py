from django.http import JsonResponse
from django.views import View
from django.utils.translation import gettext_lazy as _

from JellyBot.components.mixin import CsrfExemptMixin
from JellyBot.api.static import param
from JellyBot.views import simple_str_response
from JellyBot.components import get_root_oid
from extutils.serializer import JellyBotSerializer
from msghandle import handle_message_main
from msghandle.models import MessageEventObjectFactory


class DirectMessageWebhookView(CsrfExemptMixin, View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get(self, request, *args, **kwargs):
        msg = request.GET.get(param.Message.MESSAGE)
        if msg:
            return JsonResponse(
                handle_message_main(
                    MessageEventObjectFactory.from_direct(msg, get_root_oid(request))).to_json(),
                encoder=JellyBotSerializer)
        else:
            return simple_str_response(
                request, _(f"Provide {param.Message.MESSAGE} as a query parameter for message."))
