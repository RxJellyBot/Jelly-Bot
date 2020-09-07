# noqa
from JellyBot.components.mixin import CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.components.views import APIJsonResponseView
from JellyBot.api.responses import ShortUrlShortenResponse
from JellyBot.api.static import param
from flags import APICommand


# DEPRECATE: Remove after API v1 deprecation
class ShortUrlShortenView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                          APIJsonResponseView):  # noqa
    post_response_class = ShortUrlShortenResponse

    def get_api_action(self):
        return APICommand.SERV_SHORTEN_URL

    def mandatory_keys(self) -> set:
        return {param.Service.ShortUrl.TARGET}


# DEPRECATE: Remove after API v1 deprecation
class ShortUrlTargetChangeView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                               APIJsonResponseView):  # noqa
    post_response_class = ShortUrlShortenResponse

    def get_api_action(self):
        return APICommand.SERV_UPDATE_TARGET

    def mandatory_keys(self) -> set:
        return {param.Service.ShortUrl.TARGET, param.Service.ShortUrl.CODE}
