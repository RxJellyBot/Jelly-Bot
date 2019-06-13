from JellyBotAPI.api.responses import TokenActionCompleteApiResponse, TokenActionListApiResponse
from JellyBotAPI.api.static import param
from JellyBotAPI.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBotAPI.components.views import APIJsonResponseView


class TokenActionCompleteView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = TokenActionCompleteApiResponse

    def mandatory_keys(self) -> set:
        return set()


class TokenActionListView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = TokenActionListApiResponse

    def mandatory_keys(self) -> set:
        return {param.TokenAction.PLATFORM, param.TokenAction.USER_TOKEN}
