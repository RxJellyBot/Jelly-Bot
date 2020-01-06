from JellyBot.api.static import param
from JellyBot.api.responses import (
    PermissionQueryResponse, ProfileDetachResponse
)
from JellyBot.components.mixin import CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.views import APIJsonResponseView
from flags import APICommand


class PermissionQueryView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = PermissionQueryResponse

    def get_api_action(self):
        return APICommand.DATA_PERMISSION

    def mandatory_keys(self) -> set:
        return {param.Manage.Channel.CHANNEL_OID}


class ProfileDetachView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ProfileDetachResponse

    def get_api_action(self):
        return APICommand.MG_PROFILE_DETACH

    def mandatory_keys(self) -> set:
        return {param.Manage.Profile.PROFILE_OID}
