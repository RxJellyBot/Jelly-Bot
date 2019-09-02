from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from JellyBotAPI.keys import Session
from JellyBotAPI.api.static import result
from JellyBotAPI.components import get_root_oid
from models import APIStatisticModel
from mongodb.factory import APIStatisticsManager


class APIStatisticsCollector(MiddlewareMixin):
    # noinspection PyMethodMayBeStatic
    def process_response(self, request, response):
        api_action = request.session.pop(Session.APIStatisticsCollection.API_ACTION,
                                         APIStatisticModel.APIAction.default_value)
        dict_response = request.session.pop(Session.APIStatisticsCollection.DICT_RESPONSE,
                                            APIStatisticModel.Response.default_value)
        dict_params = request.session.pop(Session.APIStatisticsCollection.DICT_PARAMS,
                                          APIStatisticModel.Parameter.default_value)
        success = request.session.pop(Session.APIStatisticsCollection.SUCCESS,
                                      APIStatisticModel.Success.default_value
                                      if dict_params is None
                                      else dict_params.get(
                                          result.SUCCESS, APIStatisticModel.Success.default_value))
        collect = request.session.pop(Session.APIStatisticsCollection.COLLECT, False)

        path_params = None
        if request.method == "GET":
            path_params = request.GET
        elif request.method == "POST":
            path_params = request.POST

        if collect:
            rec_result = APIStatisticsManager.record_stats(
                api_action, get_root_oid(request), dict_response, dict_params, success, path_params,
                request.path_info, request.get_full_path_info()
            )

            if settings.DEBUG and not rec_result.success:
                if rec_result.exception is None:
                    raise RuntimeError(f"Stats not recorded. Result: {repr(rec_result.serialize())}")
                else:
                    raise rec_result.exception

        return response
