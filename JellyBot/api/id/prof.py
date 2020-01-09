from JellyBot.api.static import param
from JellyBot.api.responses import (
    PermissionQueryResponse, ProfileDetachResponse, ProfileNameCheckResponse, ProfileAttachResponse
)
from JellyBot.components.mixin import (
    CsrfExemptMixin, CheckParameterMixin, APIStatisticsCollectMixin
)
from JellyBot.components.views import APIJsonResponseView
from flags import APICommand


class PermissionQueryView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = PermissionQueryResponse

    def get_api_action(self):
        return APICommand.DATA_PERMISSION

    def mandatory_keys(self) -> set:
        return {param.Manage.Channel.CHANNEL_OID}


class ProfileAttachView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ProfileAttachResponse

    def get_api_action(self):
        return APICommand.MG_PROFILE_ATTACH

    def mandatory_keys(self) -> set:
        return {param.Manage.Profile.PROFILE_OID, param.Manage.Profile.CHANNEL_OID}


class ProfileDetachView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    post_response_class = ProfileDetachResponse

    def get_api_action(self):
        return APICommand.MG_PROFILE_DETACH

    def mandatory_keys(self) -> set:
        return {param.Manage.Profile.PROFILE_OID}


class ProfileNameCheckView(CsrfExemptMixin, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = ProfileNameCheckResponse

    def get_api_action(self):
        return APICommand.MG_PROFILE_NAME_CHECK

    def mandatory_keys(self) -> set:
        return {param.Manage.Profile.CHANNEL_OID, param.Manage.Profile.NAME}
