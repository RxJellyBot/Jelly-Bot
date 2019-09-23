from JellyBot.api.static import param
from JellyBot.api.responses import (
    ChannelDataQueryResponse, ChannelIssueRegisterTokenResponse, ChannelNameChangeResponse
)
from JellyBot.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.views import APIJsonResponseView
from flags import APICommand


class ChannelDataQueryView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = ChannelDataQueryResponse

    def get_api_action(self):
        return APICommand.DATA_CHANNEL

    def mandatory_keys(self) -> set:
        return {param.DataQuery.Channel.PLATFORM, param.DataQuery.Channel.CHANNEL_TOKEN}


class ChannelIssueRegistrationTokenView(
        CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ChannelIssueRegisterTokenResponse

    def get_api_action(self):
        return APICommand.MG_CHANNEL_ISSUE_REG

    def mandatory_keys(self) -> set:
        return set()


class ChannelNameChangeView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ChannelNameChangeResponse

    def get_api_action(self):
        return APICommand.MG_CHANNEL_NAME_CHANGE

    def mandatory_keys(self) -> set:
        return {param.Manage.Channel.NEW_NAME, param.Manage.Channel.CHANNEL_OID}
