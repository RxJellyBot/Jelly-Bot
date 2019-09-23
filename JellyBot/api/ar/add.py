from JellyBot.api.static import param
from JellyBot.api.responses import AutoReplyAddResponse, AutoReplyAddTokenActionResponse
from JellyBot.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.views import APIJsonResponseView
from flags import APICommand


class AutoReplyAddView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = AutoReplyAddResponse

    def get_api_action(self):
        return APICommand.AR_ADD

    def mandatory_keys(self) -> set:
        return {param.AutoReply.KEYWORD, param.AutoReply.RESPONSE}


class AutoReplyAddTokenActionView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = AutoReplyAddTokenActionResponse

    def get_api_action(self):
        return APICommand.TOKEN_AR_ADD

    def mandatory_keys(self) -> set:
        return {param.AutoReply.KEYWORD, param.AutoReply.RESPONSE}
