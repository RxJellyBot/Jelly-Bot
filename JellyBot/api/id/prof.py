# noqa
from JellyBot.api.static import param
from JellyBot.api.responses import (
    PermissionQueryResponse, ProfileDetachResponse, ProfileNameCheckResponse, ProfileAttachResponse
)
from JellyBot.components.mixin import CheckParameterMixin, APIStatisticsCollectMixin
from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.components.views import APIJsonResponseView
from flags import APICommand


# DEPRECATE: Remove after API v1 deprecation
class PermissionQueryView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                          APIJsonResponseView):  # noqa
    get_response_class = PermissionQueryResponse

    def get_api_action(self):
        return APICommand.DATA_PERMISSION

    def mandatory_keys(self) -> set:
        return {param.Manage.Channel.CHANNEL_OID}


# DEPRECATE: Remove after API v1 deprecation
class ProfileDetachView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):  # noqa
    post_response_class = ProfileDetachResponse

    def get_api_action(self):
        return APICommand.MG_PROFILE_DETACH

    def mandatory_keys(self) -> set:
        return {param.Manage.Profile.PROFILE_OID}


# DEPRECATE: Remove after API v1 deprecation
class ProfileAttachView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin, APIJsonResponseView):  # noqa
    post_response_class = ProfileAttachResponse

    def get_api_action(self):
        return APICommand.MG_PROFILE_ATTACH

    def mandatory_keys(self) -> set:
        return {param.Manage.Profile.PROFILE_OID, param.Manage.Profile.CHANNEL_OID}


# DEPRECATE: Remove after API v1 deprecation
class ProfileNameCheckView(CsrfExemptRelay, APIStatisticsCollectMixin, CheckParameterMixin,
                           APIJsonResponseView):  # noqa
    get_response_class = ProfileNameCheckResponse

    def get_api_action(self):
        return APICommand.MG_PROFILE_NAME_CHECK

    def mandatory_keys(self) -> set:
        return {param.Manage.Profile.CHANNEL_OID, param.Manage.Profile.NAME}
