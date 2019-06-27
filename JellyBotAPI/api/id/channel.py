from JellyBotAPI.api.static import param
from JellyBotAPI.api.responses import ChannelDataQueryResponse
from JellyBotAPI.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBotAPI.components.views import APIJsonResponseView
from flags import APIAction


class ChannelDataQueryView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = ChannelDataQueryResponse

    def get_api_action(self):
        return APIAction.DATA_CHANNEL

    def mandatory_keys(self) -> set:
        return {param.DataQuery.Channel.PLATFORM, param.DataQuery.Channel.CHANNEL_TOKEN}

# FIXME: FN. Channel Registration token processing service
# class ChannelIssueRegisterTokenView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
#     get_response_class = ChannelDataQueryResponse
#
#     def get_api_action(self):
#         return APIAction.DATA_CHANNEL
#
#     def mandatory_keys(self) -> set:
#         return {param.DataQuery.Channel.PLATFORM, param.DataQuery.Channel.CHANNEL_TOKEN}
