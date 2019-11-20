from flags import APICommand
from JellyBot.api.responses import ExecodeCompleteApiResponse, ExecodeListApiResponse
from JellyBot.api.static import param
from JellyBot.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.views import APIJsonResponseView


class ExecodeCompleteView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ExecodeCompleteApiResponse

    def get_api_action(self):
        return APICommand.EXECODE_COMPLETE

    def mandatory_keys(self) -> set:
        return set()


class ExecodeListView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = ExecodeListApiResponse

    def get_api_action(self):
        return APICommand.EXECODE_LIST

    def mandatory_keys(self) -> set:
        return {param.Execode.PLATFORM, param.Execode.USER_TOKEN}
