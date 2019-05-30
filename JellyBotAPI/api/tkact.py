from django.views.generic.base import View

from JellyBotAPI.api.static import param
from components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin


class TokenProcessingView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, View):
    def mandatory_keys(self) -> list:
        return [param.TokenAction.TOKEN]

    def post(self, request, *args, **kwargs):
        # INCOMPLETE: Get token and check required params

        # request.session[keys.APIStatisticsCollection.API_ACTION] = APIAction.AR_ADD
        # request.session[keys.APIStatisticsCollection.DICT_PARAMS] = param_dict
        # request.session[keys.APIStatisticsCollection.DICT_RESPONSE] = response_json_dict
        # request.session[keys.APIStatisticsCollection.SUCCESS] = response_json_dict.get(result.SUCCESS, False)

        return None
