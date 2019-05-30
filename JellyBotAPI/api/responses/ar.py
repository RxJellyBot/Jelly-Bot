from django.http import QueryDict

from JellyBotAPI import SystemConfig
from JellyBotAPI.api.static import result, info, param
from flags import AutoReplyContentType, TokenAction
from models import AutoReplyConnectionModel
from mongodb.factory import (
    GetOutcome, InsertOutcome,
    AutoReplyConnectionManager, AutoReplyContentManager, MixedUserManager, TokenActionManager
)

from ._base import BaseApiResponse


class AutoReplyAddBaseResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        self._param_dict = {
            param.AutoReply.KEYWORD: param_dict.get(param.AutoReply.KEYWORD),
            param.AutoReply.KEYWORD_TYPE: param_dict.get(param.AutoReply.KEYWORD_TYPE),
            param.AutoReply.RESPONSE: param_dict.getlist(param.AutoReply.RESPONSE),
            param.AutoReply.RESPONSE_TYPE: param_dict.getlist(param.AutoReply.RESPONSE_TYPE),
            param.AutoReply.CREATOR_TOKEN: param_dict.get(param.AutoReply.CREATOR_TOKEN),
            param.AutoReply.PLATFORM: param_dict.get(param.AutoReply.PLATFORM),
            param.AutoReply.PRIVATE: param_dict.get(param.AutoReply.PRIVATE, False),
            param.AutoReply.PINNED: param_dict.get(param.AutoReply.PINNED, False),
            param.AutoReply.COOLDOWN: param_dict.get(param.AutoReply.COOLDOWN, 0),
        }

        self._keyword = self._param_dict[param.AutoReply.KEYWORD]
        self._keyword_type = self._param_dict[param.AutoReply.KEYWORD_TYPE]
        self._responses = self._param_dict[param.AutoReply.RESPONSE]
        self._response_types = self._param_dict[param.AutoReply.RESPONSE_TYPE]
        self._creator_token = self._param_dict[param.AutoReply.CREATOR_TOKEN]
        self._platform = self._param_dict[param.AutoReply.PLATFORM]
        self._private = self._param_dict[param.AutoReply.PRIVATE]
        self._pinned = self._param_dict[param.AutoReply.PINNED]
        self._cooldown = self._param_dict[param.AutoReply.COOLDOWN]

        self._err = dict()
        self._data = dict()
        self._flag = dict()
        self._info = list()
        self._result = None

    def _handle_keyword(self):
        k = result.AutoReplyResponse.KEYWORD
        r = AutoReplyContentManager.get_content(self._keyword, int(AutoReplyContentType.TEXT or self._keyword_type))
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
            self._response_types = self._response_types + [AutoReplyContentType.TEXT] * diff
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

    def _handle_creator_oid(self):
        k = result.AutoReplyResponse.CREATOR_OID
        r = MixedUserManager.register_onplat(self._platform, self._creator_token)
        if GetOutcome.is_success(r.outcome):
            self._data[k] = r.model.id.value
        else:
            self._err[k] = r.serialize()

    def _handle_platform(self):
        k = result.AutoReplyResponse.PLATFORM
        if self._platform is None:
            self._err[k] = None
        else:
            self._flag[k] = self._platform

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
        self._platform = int(self._platform)

        self._handle_keyword()
        self._handle_responses()
        self._handle_creator_oid()
        self._handle_platform()
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
            return len(self._err) == 0 and \
                   InsertOutcome.is_success(self._result.outcome) and \
                   (self._creator_token is not None) and \
                   (self._platform is not None)
        except AttributeError:
            return False

    @property
    def param_dict(self) -> dict:
        return self._param_dict


class AutoReplyAddResponse(AutoReplyAddBaseResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)
        self._param_dict[param.AutoReply.CHANNEL_TOKEN] = param_dict.get(param.AutoReply.CHANNEL_TOKEN)

        self._channel_token = self._param_dict[param.AutoReply.CHANNEL_TOKEN]

    def _handle_channel(self):
        k = result.AutoReplyResponse.CHANNEL
        if self._channel_token is None:
            self._err[k] = None
        else:
            self._flag[k] = self._channel_token

    def pre_process(self):
        super().pre_process()

        self._handle_channel()

        if len(self._err) == 0:
            self._result = AutoReplyConnectionManager.add(
                self._data[result.AutoReplyResponse.KEYWORD],
                self._data[result.AutoReplyResponse.RESPONSES],
                self._data[result.AutoReplyResponse.CREATOR_OID],
                self._flag[result.AutoReplyResponse.PLATFORM],
                self._flag[result.AutoReplyResponse.CHANNEL],
                self._flag[result.AutoReplyResponse.PINNED],
                self._flag[result.AutoReplyResponse.PRIVATE],
                self._flag[result.AutoReplyResponse.COOLDOWN_SEC])

    def is_success(self) -> bool:
        return super().is_success() and (self._channel_token is not None)


class AutoReplyAddTokenActionResponse(AutoReplyAddBaseResponse):
    def pre_process(self):
        super().pre_process()

        if len(self._err) == 0:
            self._result = TokenActionManager.enqueue_action_ar_add(
                TokenAction.AR_ADD, AutoReplyConnectionModel,
                keyword_oid=self._data[result.AutoReplyResponse.KEYWORD],
                responses_oids=self._data[result.AutoReplyResponse.RESPONSES],
                creator_oid=self._data[result.AutoReplyResponse.CREATOR_OID],
                pinned=self._flag[result.AutoReplyResponse.PINNED], disabled=False,
                private=self._flag[result.AutoReplyResponse.PRIVATE],
                cooldown_sec=self._flag[result.AutoReplyResponse.COOLDOWN_SEC])
