from JellyBotAPI.api.static import param
from JellyBotAPI.api.responses import ContentValidationResponse
from JellyBotAPI.components.mixin import CsrfExemptMixin, CheckParameterMixin
from JellyBotAPI.components.views import APIJsonResponseView


class ContentValidationView(CsrfExemptMixin, CheckParameterMixin, APIJsonResponseView):
    get_response_class = ContentValidationResponse

    def mandatory_keys(self) -> set:
        return {param.Validation.CONTENT, param.Validation.CONTENT_TYPE}
