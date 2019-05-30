import json

from django.http import JsonResponse
from django.views import View

from JellyBotAPI import keys
from extutils.decorators import abstractproperty
from extutils.serializer import JellyBotAPISerializer


class APIJsonResponseView(View):
    @abstractproperty
    def response_class(self) -> type:
        return object

    # noinspection PyCallingNonCallable
    def post(self, request, *args, **kwargs):
        response_api = self.__class__.response_class(request.POST)

        response_http = JsonResponse(response_api.to_dict(), encoder=JellyBotAPISerializer)

        response_json_dict = json.loads(response_http.content)

        request.session[keys.APIStatisticsCollection.DICT_PARAMS] = response_api.param_dict
        request.session[keys.APIStatisticsCollection.DICT_RESPONSE] = response_json_dict

        return response_http
