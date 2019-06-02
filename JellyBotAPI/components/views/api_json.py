import json

from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View

from JellyBotAPI import keys
from extutils.serializer import JellyBotAPISerializer


class APIJsonResponseView(View):
    @property
    def get_response_class(self) -> type:
        return type(None)

    @property
    def post_response_class(self) -> type:
        return type(None)

    # noinspection PyTypeChecker
    @property
    def allowed_response_classes(self) -> list:
        lst = []
        if not issubclass(self.__class__.get_response_class, type(None)):
            lst.append("GET")

        if not issubclass(self.__class__.post_response_class, type(None)):
            lst.append("POST")

        return lst

    # noinspection PyCallingNonCallable, PyTypeChecker
    def get(self, request, *args, **kwargs):
        if issubclass(self.__class__.get_response_class, type(None)):
            return HttpResponseNotAllowed(self.allowed_response_classes)
        else:
            response_api = self.__class__.get_response_class(request.GET)

            return self.process_api_response(request, response_api, *args, **kwargs)

    # noinspection PyCallingNonCallable, PyTypeChecker
    def post(self, request, *args, **kwargs):
        if issubclass(self.__class__.post_response_class, type(None)):
            return HttpResponseNotAllowed(self.allowed_response_classes)
        else:
            response_api = self.__class__.post_response_class(request.POST)

            return self.process_api_response(request, response_api, *args, **kwargs)

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def process_api_response(self, request, response_api, *args, **kwargs):
        response_http = JsonResponse(response_api.to_dict(), encoder=JellyBotAPISerializer)

        response_json_dict = json.loads(response_http.content)

        request.session[keys.APIStatisticsCollection.DICT_PARAMS] = response_api.param_dict
        request.session[keys.APIStatisticsCollection.DICT_RESPONSE] = response_json_dict

        return response_http
