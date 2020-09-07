from JellyBot.components.mixin import APIStatisticsCollectMixin, CheckParameterMixin
from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.components.views import APIJsonResponseView
from JellyBot.api.responses import AutoReplyTagPopularityResponse

from flags import APICommand


# DEPRECATE: Remove after API v1 deprecation
class AutoReplyTagPopularityQueryView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                                      APIJsonResponseView):  # noqa
    get_response_class = AutoReplyTagPopularityResponse

    def get_api_action(self):
        return APICommand.AR_TAG_POP

    def mandatory_keys(self) -> set:
        return set()
