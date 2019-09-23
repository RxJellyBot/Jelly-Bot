from flags import APICommand
from JellyBot.api.responses import TokenActionCompleteApiResponse, TokenActionListApiResponse
from JellyBot.api.static import param
from JellyBot.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.views import APIJsonResponseView


class TokenActionCompleteView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = TokenActionCompleteApiResponse

    def get_api_action(self):
        return APICommand.TOKEN_COMPLETE

    def mandatory_keys(self) -> set:
        return set()


class TokenActionListView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = TokenActionListApiResponse

    def get_api_action(self):
        return APICommand.TOKEN_LIST

    def mandatory_keys(self) -> set:
        return {param.TokenAction.PLATFORM, param.TokenAction.USER_TOKEN}
