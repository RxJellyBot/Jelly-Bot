from JellyBotAPI.api.responses import TokenActionApiResponse
from JellyBotAPI.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBotAPI.components.views import APIJsonResponseView


class TokenProcessingView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    # INCOMPLETE: Token: Get token and check required params
    post_response_class = TokenActionApiResponse

    def mandatory_keys(self) -> set:
        return set()
