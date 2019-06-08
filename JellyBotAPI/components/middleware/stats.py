from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from JellyBotAPI import keys
from JellyBotAPI.api.static import result
from flags import APIAction
from mongodb.factory import InsertOutcome, APIStatisticsManager


class APIStatisticsCollector(MiddlewareMixin):
    # noinspection PyMethodMayBeStatic
    def process_response(self, request, response):
        api_action = request.session.pop(keys.APIStatisticsCollection.API_ACTION, APIAction.UNKNOWN)
        dict_response = request.session.pop(keys.APIStatisticsCollection.DICT_RESPONSE, None)
        dict_params = request.session.pop(keys.APIStatisticsCollection.DICT_PARAMS, None)
        success = request.session.pop(keys.APIStatisticsCollection.SUCCESS,
                                      False if dict_params is None else dict_params.get(result.SUCCESS, False))
        collect = request.session.pop(keys.APIStatisticsCollection.COLLECT, False)

        path_params = None
        if request.method == "GET":
            path_params = request.GET
        elif request.method == "POST":
            path_params = request.POST

        if collect:
            rec_result = APIStatisticsManager.record_stats(
                api_action, dict_response, dict_params, success, path_params,
                request.path_info, request.get_full_path_info()
            )

            if settings.DEBUG and not InsertOutcome.is_success(rec_result.outcome):
                if rec_result.exception is None:
                    raise RuntimeError(f"Stats not recorded. Result: {repr(rec_result.serialize())}")
                else:
                    raise rec_result.exception

        return response
