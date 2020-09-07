# noqa
from flags import APICommand
from JellyBot.api.responses import ExecodeCompleteApiResponse, ExecodeListApiResponse
from JellyBot.api.static import param
from JellyBot.components.mixin import CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.components.views import APIJsonResponseView


# DEPRECATE: Remove after API v1 deprecation
class ExecodeCompleteView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                          APIJsonResponseView):  # noqa
    post_response_class = ExecodeCompleteApiResponse

    def get_api_action(self):
        return APICommand.EXECODE_COMPLETE

    def mandatory_keys(self) -> set:
        return set()


# DEPRECATE: Remove after API v1 deprecation
class ExecodeListView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):  # noqa
    get_response_class = ExecodeListApiResponse

    def get_api_action(self):
        return APICommand.EXECODE_LIST

    def mandatory_keys(self) -> set:
        return {param.Execode.PLATFORM, param.Execode.USER_TOKEN}
