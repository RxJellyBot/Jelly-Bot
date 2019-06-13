from django.http import QueryDict

from extutils import is_empty_string
from JellyBotAPI.api.static import param, result
from flags import AutoReplyContentType
from models.validators import AutoReplyValidators

from .._base import BaseApiResponse


class ContentValidationResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)
        self._param_dict = {
            param.Validation.CONTENT: param_dict.get(param.Validation.CONTENT),
            param.Validation.CONTENT_TYPE: param_dict.get(param.Validation.CONTENT_TYPE)
        }

        self._content = self._param_dict[param.Validation.CONTENT]
        self._content_type = self._param_dict[param.Validation.CONTENT_TYPE]

        self._result = False

    # noinspection PyBroadException,PyArgumentList
    def _handle_content_type(self):
        k = param.Validation.CONTENT_TYPE

        if self._content_type is None:
            self._err[k] = None
        else:
            try:
                self._data[k] = AutoReplyContentType(int(self._content_type))
            except Exception:
                self._err[k] = self._content_type

    def _handle_content(self):
        k = param.Validation.CONTENT
        self._data[k] = self._content

    def is_success(self) -> bool:
        return not is_empty_string(self._content) and \
               not is_empty_string(self._content_type) and \
               self._result

    def pre_process(self):
        self._handle_content_type()
        self._handle_content()

    def process_ifnoerror(self):
        self._result = AutoReplyValidators.is_valid_content(self._data[param.Validation.CONTENT_TYPE],
                                                            self._data[param.Validation.CONTENT])

    def serialize_success(self) -> dict:
        return {result.DATA: self._data}

    def serialize_failed(self) -> dict:
        return {result.ERRORS: self._err}

    def serialize_extra(self) -> dict:
        return {result.RESULT: self._result}
