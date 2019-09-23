from JellyBot.components.mixin import CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin
from JellyBot.components.views import APIJsonResponseView
from JellyBot.api.responses import AutoReplyTagPopularityResponse

from flags import APICommand


class AutoReplyTagPopularityQueryView(
        CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = AutoReplyTagPopularityResponse

    def get_api_action(self):
        return APICommand.AR_TAG_POP

    def mandatory_keys(self) -> set:
        return set()
