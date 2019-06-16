from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from JellyBotAPI import keys
from JellyBotAPI.api.static import result
from JellyBotAPI.components import get_root_oid
from models import APIStatisticModel
from mongodb.factory import APIStatisticsManager


class APIStatisticsCollector(MiddlewareMixin):
    # noinspection PyMethodMayBeStatic
    def process_response(self, request, response):
        _default_dict = APIStatisticModel.get_default_dict()

        api_action = request.session.pop(keys.APIStatisticsCollection.API_ACTION,
                                         _default_dict.get(APIStatisticModel.APIAction))
        dict_response = request.session.pop(keys.APIStatisticsCollection.DICT_RESPONSE,
                                            _default_dict.get(APIStatisticModel.Response))
        dict_params = request.session.pop(keys.APIStatisticsCollection.DICT_PARAMS,
                                          _default_dict.get(APIStatisticModel.Parameter))
        success = request.session.pop(keys.APIStatisticsCollection.SUCCESS,
                                      _default_dict.get(
                                          APIStatisticModel.Success) if dict_params is None else dict_params.get(
                                          result.SUCCESS, _default_dict.get(APIStatisticModel.Success)))
        collect = request.session.pop(keys.APIStatisticsCollection.COLLECT, False)

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
