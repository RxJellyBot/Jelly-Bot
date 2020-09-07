# noqa
from JellyBot.api.static import param
from JellyBot.api.responses import (
    ChannelDataQueryResponse, ChannelIssueRegisterExecodeResponse, ChannelNameChangeResponse, ChannelStarChangeResponse
)
from JellyBot.components.mixin import CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.components.views import APIJsonResponseView
from flags import APICommand


# DEPRECATE: Remove after API v1 deprecation
class ChannelDataQueryView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                           APIJsonResponseView):  # noqa
    get_response_class = ChannelDataQueryResponse

    def get_api_action(self):
        return APICommand.DATA_CHANNEL

    def mandatory_keys(self) -> set:
        return {param.DataQuery.Channel.PLATFORM, param.DataQuery.Channel.CHANNEL_TOKEN}


# DEPRECATE: Remove after API v1 deprecation
class ChannelIssueRegistrationExecodeView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                                          APIJsonResponseView):  # noqa
    post_response_class = ChannelIssueRegisterExecodeResponse

    def get_api_action(self):
        return APICommand.MG_CHANNEL_ISSUE_REG

    def mandatory_keys(self) -> set:
        return set()


# DEPRECATE: Remove after API v1 deprecation
class ChannelNameChangeView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                            APIJsonResponseView):  # noqa
    post_response_class = ChannelNameChangeResponse

    def get_api_action(self):
        return APICommand.MG_CHANNEL_NAME_CHANGE

    def mandatory_keys(self) -> set:
        return {param.Manage.Channel.NEW_NAME, param.Manage.Channel.CHANNEL_OID}


# DEPRECATE: Remove after API v1 deprecation
class ChannelStarChangeView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                            APIJsonResponseView):  # noqa
    post_response_class = ChannelStarChangeResponse

    def get_api_action(self):
        return APICommand.MG_CHANNEL_STAR_CHANGE

    def mandatory_keys(self) -> set:
        return {param.Manage.Channel.STAR, param.Manage.Channel.CHANNEL_OID}
