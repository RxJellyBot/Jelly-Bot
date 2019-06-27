from JellyBotAPI.api.static import param
from JellyBotAPI.api.responses import AutoReplyAddResponse, AutoReplyAddTokenActionResponse
from JellyBotAPI.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBotAPI.components.views import APIJsonResponseView
from flags import APIAction


class AutoReplyAddView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = AutoReplyAddResponse

    def get_api_action(self):
        return APIAction.AR_ADD

    def mandatory_keys(self) -> set:
        return {param.AutoReply.KEYWORD, param.AutoReply.RESPONSE}


class AutoReplyAddTokenActionView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = AutoReplyAddTokenActionResponse

    def get_api_action(self):
        return APIAction.TOKEN_AR_ADD

    def mandatory_keys(self) -> set:
        return {param.AutoReply.KEYWORD, param.AutoReply.RESPONSE}
