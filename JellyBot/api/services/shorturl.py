from JellyBot.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.views import APIJsonResponseView
from JellyBot.api.responses import ShortUrlShortenResponse
from JellyBot.api.static import param
from flags import APICommand


class ShortUrlShortenView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ShortUrlShortenResponse

    def get_api_action(self):
        return APICommand.SERV_SHORTEN_URL

    def mandatory_keys(self) -> set:
        return {param.Service.ShortUrl.TARGET}


class ShortUrlTargetChangeView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ShortUrlShortenResponse

    def get_api_action(self):
        return APICommand.SERV_UPDATE_TARGET

    def mandatory_keys(self) -> set:
        return {param.Service.ShortUrl.TARGET, param.Service.ShortUrl.CODE}
