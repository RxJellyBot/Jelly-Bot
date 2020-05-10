from JellyBot.api.static import param, result
from JellyBot.api.responses.mixin import SerializeErrorMixin, SerializeResultExtraMixin
from flags import AutoReplyContentType
from models.utils import AutoReplyValidator

from .._base import BaseApiResponse


class ContentValidationResponse(SerializeErrorMixin, SerializeResultExtraMixin, BaseApiResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)
        self._param_dict.update(**{
            param.Validation.CONTENT: param_dict.get(param.Validation.CONTENT),
            param.Validation.CONTENT_TYPE: param_dict.get(param.Validation.CONTENT_TYPE)
        })

        self._content = self._param_dict[param.Validation.CONTENT]
        self._content_type = self._param_dict[param.Validation.CONTENT_TYPE]

        self._result = False

    # noinspection PyBroadException,PyArgumentList
    def _handle_content_type_(self):
        k = param.Validation.CONTENT_TYPE

        if self._content_type is None:
            self._err[k] = None
        else:
            try:
                self._data[k] = AutoReplyContentType(int(self._content_type))
            except Exception:
                self._err[k] = self._content_type

    def _handle_content_(self):
        k = param.Validation.CONTENT
        self._data[k] = self._content

    def pass_condition(self) -> bool:
        return self._content and self._content_type and self._result

    def pre_process(self):
        self._handle_content_type_()
        self._handle_content_()

    def process_pass(self):
        self._result = AutoReplyValidator.is_valid_content(self._data[param.Validation.CONTENT_TYPE],
                                                           self._data[param.Validation.CONTENT])

    def serialize_success(self) -> dict:
        return {result.DATA: self._data}
