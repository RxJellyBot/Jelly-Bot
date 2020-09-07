# noqa
from JellyBot.api.static import param
from JellyBot.api.responses import AutoReplyAddResponse, AutoReplyAddExecodeResponse
from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.components.mixin import CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.views import APIJsonResponseView
from flags import APICommand


# DEPRECATE: Remove after API v1 deprecation
class AutoReplyAddView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):  # noqa
    post_response_class = AutoReplyAddResponse

    def get_api_action(self):
        return APICommand.AR_ADD

    def mandatory_keys(self) -> set:
        return {param.AutoReply.KEYWORD, param.AutoReply.RESPONSE}


# DEPRECATE: Remove after API v1 deprecation
class AutoReplyAddExecodeView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                              APIJsonResponseView):  # noqa
    post_response_class = AutoReplyAddExecodeResponse

    def get_api_action(self):
        return APICommand.EXECODE_AR_ADD

    def mandatory_keys(self) -> set:
        return {param.AutoReply.KEYWORD, param.AutoReply.RESPONSE}
