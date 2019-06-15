from abc import ABC

from django.http import QueryDict

from extutils import is_empty_string
from JellyBotAPI import SystemConfig
from JellyBotAPI.api.static import result, info, param
from extutils import cast_keep_none
from flags import AutoReplyContentType, TokenAction
from models import AutoReplyConnectionModel
from mongodb.factory import (
    AutoReplyConnectionManager, AutoReplyContentManager, MixedUserManager, TokenActionManager
)
from mongodb.factory.results import GetOutcome, InsertOutcome

from .._base import BaseApiResponse


class AutoReplyAddBaseResponse(BaseApiResponse, ABC):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)
        self._param_dict = {
            param.AutoReply.KEYWORD: param_dict.get(param.AutoReply.KEYWORD),
            param.AutoReply.KEYWORD_TYPE: param_dict.get(param.AutoReply.KEYWORD_TYPE),
            param.AutoReply.RESPONSE: param_dict.getlist(param.AutoReply.RESPONSE),
            param.AutoReply.RESPONSE_TYPE: param_dict.getlist(param.AutoReply.RESPONSE_TYPE),
            param.AutoReply.CREATOR_TOKEN: param_dict.get(param.AutoReply.CREATOR_TOKEN),
            param.AutoReply.PRIVATE: cast_keep_none(param_dict.get(param.AutoReply.PRIVATE), bool),
            param.AutoReply.PINNED: cast_keep_none(param_dict.get(param.AutoReply.PINNED), bool),
            param.AutoReply.COOLDOWN: int(
                param_dict.get(param.AutoReply.COOLDOWN, AutoReplyConnectionModel.get_default_dict().get(
                    AutoReplyConnectionModel.CoolDownSeconds))),
        }

        self._keyword = self._param_dict[param.AutoReply.KEYWORD]
        self._keyword_type = self._param_dict[param.AutoReply.KEYWORD_TYPE]
        self._responses = self._param_dict[param.AutoReply.RESPONSE]
        self._response_types = self._param_dict[param.AutoReply.RESPONSE_TYPE]
        self._creator_token = self._param_dict[param.AutoReply.CREATOR_TOKEN]
        self._private = self._param_dict[param.AutoReply.PRIVATE]
        self._pinned = self._param_dict[param.AutoReply.PINNED]
        self._cooldown = self._param_dict[param.AutoReply.COOLDOWN]
        self._is_local = bool(param_dict.get(param.LOCAL_REFER, False))

    def _handle_keyword(self):
        k = result.AutoReplyResponse.KEYWORD
        r = AutoReplyContentManager.get_content(self._keyword,
                                                int(AutoReplyContentType.default() or self._keyword_type))
        if GetOutcome.is_success(r.outcome):
            self._data[k] = r.model.id.value
        else:
            self._err[k] = r.serialize()

    def _handle_responses(self):
        k = result.AutoReplyResponse.RESPONSES
        resp_err = dict()
        resp_list = list()

        if len(self._responses) > SystemConfig.AutoReply.MAX_CONTENT_LENGTH:
            self._responses = self._responses[:SystemConfig.AutoReply.MAX_CONTENT_LENGTH]
            self._info.append(info.AutoReply.RESPONSES_TRUNCATED)

        resp_len = len(self._responses)
        type_len = len(self._response_types)
        diff = resp_len - type_len
        if diff > 0:
            self._response_types = self._response_types + [AutoReplyContentType.default()] * diff
            self._info.append(info.AutoReply.RESPONSE_TYPES_LENGTHENED)
        elif diff < 0:
            self._response_types = self._response_types[:-diff]
            self._info.append(info.AutoReply.RESPONSE_TYPES_SHORTENED)

        for idx, resp in enumerate(self._responses):
            r = AutoReplyContentManager.get_content(resp, self._response_types[idx])

            resp_outcome = r.outcome
            if GetOutcome.is_success(resp_outcome):
                resp_list.append(r.model.id.value)
            else:
                resp_err[idx] = r.serialize()

        if len(resp_err) > 0:
            self._err[k] = resp_err
        else:
            self._data[k] = resp_list

    def get_user_model(self):
        raise NotImplementedError()

    def _handle_creator_oid(self):
        k = result.AutoReplyResponse.CREATOR_OID

        r = self.get_user_model()

        if GetOutcome.is_success(r.outcome):
            self._data[k] = r.model.id.value
        else:
            self._err[k] = r.serialize()

    def _handle_pinned(self):
        k = result.AutoReplyResponse.PINNED
        self._flag[k] = self._pinned

    def _handle_private(self):
        k = result.AutoReplyResponse.PRIVATE
        self._flag[k] = self._private

    def _handle_cooldown(self):
        k = result.AutoReplyResponse.COOLDOWN_SEC
        self._flag[k] = self._cooldown

    def pre_process(self):
        self._handle_keyword()
        self._handle_responses()
        self._handle_creator_oid()
        self._handle_pinned()
        self._handle_private()
        self._handle_cooldown()

    def serialize_success(self) -> dict:
        return {result.DATA: self._data, result.RESULT: self._result}

    def serialize_failed(self) -> dict:
        return {result.ERRORS: self._err}

    def serialize_extra(self) -> dict:
        return {result.FLAGS: self._flag, result.INFO: self._info}

    def is_success(self) -> bool:
        try:
            return super().is_success() and \
                   InsertOutcome.is_success(self._result.outcome) and \
                   not is_empty_string(self._creator_token)
        except AttributeError:
            return False

    @property
    def param_dict(self) -> dict:
        return self._param_dict


class AutoReplyAddResponse(AutoReplyAddBaseResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)
        self._param_dict[param.AutoReply.CHANNEL_TOKEN] = param_dict.get(param.AutoReply.CHANNEL_TOKEN)
        self._param_dict[param.AutoReply.PLATFORM] = param_dict.get(param.AutoReply.PLATFORM)

        self._channel_token = self._param_dict[param.AutoReply.CHANNEL_TOKEN]
        self._platform = self._param_dict[param.AutoReply.PLATFORM]

    def get_user_model(self):
        if self._is_local:
            return MixedUserManager.get_user_data_api_token(self._creator_token)
        else:
            return MixedUserManager.register_onplat(self._platform, self._creator_token)

    def _handle_platform(self):
        k = result.AutoReplyResponse.PLATFORM
        if self._platform is None:
            self._err[k] = None
        else:
            self._flag[k] = int(self._platform)

    def _handle_channel(self):
        k = result.AutoReplyResponse.CHANNEL
        if self._channel_token is None:
            self._err[k] = None
        else:
            self._flag[k] = self._channel_token

    def pre_process(self):
        super().pre_process()

        self._handle_channel()
        self._handle_platform()

    def process_ifnoerror(self):
        self._result = AutoReplyConnectionManager.add_conn(
            self._data[result.AutoReplyResponse.KEYWORD],
            self._data[result.AutoReplyResponse.RESPONSES],
            self._data[result.AutoReplyResponse.CREATOR_OID],
            self._flag[result.AutoReplyResponse.PLATFORM],
            self._flag[result.AutoReplyResponse.CHANNEL],
            self._flag[result.AutoReplyResponse.PINNED],
            self._flag[result.AutoReplyResponse.PRIVATE],
            self._flag[result.AutoReplyResponse.COOLDOWN_SEC])

    def is_success(self) -> bool:
        return super().is_success() and \
               not is_empty_string(self._channel_token) and \
               (self._platform is not None)


class AutoReplyAddTokenActionResponse(AutoReplyAddBaseResponse):
    def get_user_model(self):
        return MixedUserManager.get_user_data_api_token(self._creator_token)

    def process_ifnoerror(self):
        self._result = TokenActionManager.enqueue_action(
            self._data[result.AutoReplyResponse.CREATOR_OID],
            TokenAction.AR_ADD, AutoReplyConnectionModel,
            keyword_oid=self._data[result.AutoReplyResponse.KEYWORD],
            responses_oids=self._data[result.AutoReplyResponse.RESPONSES],
            creator_oid=self._data[result.AutoReplyResponse.CREATOR_OID],
            pinned=self._flag[result.AutoReplyResponse.PINNED], disabled=False,
            private=self._flag[result.AutoReplyResponse.PRIVATE],
            cooldown_sec=self._flag[result.AutoReplyResponse.COOLDOWN_SEC])
