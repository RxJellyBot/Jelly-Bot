from JellyBot.api.static import param
from JellyBot.api.responses import ContentValidationResponse
from JellyBot.components.mixin import CsrfExemptMixin, CheckParameterMixin
from JellyBot.components.views import APIJsonResponseView


class ContentValidationView(CsrfExemptMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = ContentValidationResponse

    def mandatory_keys(self) -> set:
        return {param.Validation.CONTENT, param.Validation.CONTENT_TYPE}
