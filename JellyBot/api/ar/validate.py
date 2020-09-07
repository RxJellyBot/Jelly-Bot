# noqa
from JellyBot.api.static import param
from JellyBot.api.responses import ContentValidationResponse
from JellyBot.components.mixin import CheckParameterMixin
from JellyBot.components.relay import CsrfExemptRelay
from JellyBot.components.views import APIJsonResponseView


# DEPRECATE: Remove after API v1 deprecation
class ContentValidationView(CsrfExemptRelay, CheckParameterMixin, APIJsonResponseView):  # noqa
    get_response_class = ContentValidationResponse

    def mandatory_keys(self) -> set:
        return {param.Validation.CONTENT, param.Validation.CONTENT_TYPE}
