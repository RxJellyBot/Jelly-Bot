from abc import ABC

from JellyBot import systemconfig
from JellyBot.api.static import result, info, param
from JellyBot.api.responses import BaseApiResponse
from JellyBot.api.responses.mixin import (
    HandleChannelOidMixin, SerializeErrorMixin, RequireSenderMixin, SerializeResultExtraMixin
)
from extutils import cast_keep_none
from flags import AutoReplyContentType, Execode
from models import AutoReplyModuleModel, AutoReplyModuleExecodeModel, AutoReplyContentModel
from mongodb.factory import (
    AutoReplyManager, ExecodeManager
)
from mongodb.factory.results import WriteOutcome


class AutoReplyAddBaseResponse(
        RequireSenderMixin, SerializeErrorMixin, SerializeResultExtraMixin, BaseApiResponse, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)
        self._param_dict.update(**{
            param.AutoReply.KEYWORD: param_dict.get(param.AutoReply.KEYWORD),
            param.AutoReply.KEYWORD_TYPE: param_dict.get(param.AutoReply.KEYWORD_TYPE),
            param.AutoReply.RESPONSE: param_dict.getlist(param.AutoReply.RESPONSE),
            param.AutoReply.RESPONSE_TYPE: param_dict.getlist(param.AutoReply.RESPONSE_TYPE),
            param.AutoReply.PRIVATE: cast_keep_none(param_dict.get(param.AutoReply.PRIVATE), bool),
            param.AutoReply.PINNED: cast_keep_none(param_dict.get(param.AutoReply.PINNED), bool),
            param.AutoReply.TAGS: param_dict.get(param.AutoReply.TAGS),
            param.AutoReply.COOLDOWN: int(
                param_dict.get(param.AutoReply.COOLDOWN, AutoReplyModuleModel.CooldownSec.default_value)
            )
        })

        self._keyword = self._param_dict[param.AutoReply.KEYWORD]
        self._keyword_type = self._param_dict[param.AutoReply.KEYWORD_TYPE]
        self._responses = self._param_dict[param.AutoReply.RESPONSE]
        self._response_types = self._param_dict[param.AutoReply.RESPONSE_TYPE]
        self._private = self._param_dict[param.AutoReply.PRIVATE]
        self._pinned = self._param_dict[param.AutoReply.PINNED]
        self._tags = self._param_dict[param.AutoReply.TAGS]
        self._cooldown = self._param_dict[param.AutoReply.COOLDOWN]
        self._is_local = bool(param_dict.get(param.LOCAL_REFER, False))

    def _handle_keyword_(self):
        self._handle_keyword_type_()

        k = result.AutoReplyResponse.KEYWORD
        self._data[k] = self._keyword

    def _handle_keyword_type_(self):
        self._keyword_type = int(AutoReplyContentType.default() or self._keyword_type)

        if self._keyword_type == AutoReplyContentType.IMAGE:
            self._err[result.AutoReplyResponse.KEYWORD] = False

    def _handle_responses_(self):
        k = result.AutoReplyResponse.RESPONSES

        if len(self._responses) > systemconfig.AutoReply.MaxContentLength:
            self._responses = self._responses[:systemconfig.AutoReply.MaxContentLength]
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

        self._responses = self._data[k] = \
            [AutoReplyContentModel(Content=resp, ContentType=int(self._response_types[idx]))
             for idx, resp in enumerate(self._responses)]

    def _handle_private_(self):
        k = result.AutoReplyResponse.PRIVATE
        self._flag[k] = self._private

    def _handle_pinned_(self):
        k = result.AutoReplyResponse.PINNED
        self._flag[k] = self._pinned

    def _handle_tags_(self):
        k = result.AutoReplyResponse.TAGS

        if self._tags:
            # Tag string to array
            # noinspection PyUnresolvedReferences
            tags = self._tags.split(systemconfig.AutoReply.TagSplittor)
            tag_ids = []

            for tag in tags:
                # Replace tag name with its `ObjectId`
                tres = AutoReplyManager.tag_get_insert(tag)
                if tres.outcome.is_success:
                    tag_ids.append(tres.model.id)

            self._tags = tag_ids

        self._flag[k] = self._tags

    def _handle_cooldown_(self):
        k = result.AutoReplyResponse.COOLDOWN_SEC
        self._flag[k] = self._cooldown

    def pre_process(self):
        self._handle_keyword_()
        self._handle_responses_()
        self._handle_pinned_()
        self._handle_private_()
        self._handle_tags_()
        self._handle_cooldown_()

    def serialize_success(self) -> dict:
        d = super().serialize_success()
        d[result.DATA] = self._data
        return d

    def serialize_extra(self) -> dict:
        d = super().serialize_extra()
        d.update(**{result.FLAGS: self._flag, result.INFO: self._info})
        return d

    @property
    def param_dict(self) -> dict:
        return self._param_dict


class AutoReplyAddResponse(HandleChannelOidMixin, AutoReplyAddBaseResponse):
    def process_pass(self):
        self._result = AutoReplyManager.add_conn_complete(
            self._keyword, self._keyword_type, self._responses, self._sender_oid, self.get_channel_oid(),
            self._pinned, self._private, self._tags, self._cooldown)

    def is_success(self) -> bool:
        try:
            return super().is_success() and self._result.outcome == WriteOutcome.O_INSERTED
        except AttributeError:
            return False


class AutoReplyAddExecodeResponse(AutoReplyAddBaseResponse):
    def process_pass(self):
        self._result = ExecodeManager.enqueue_execode(
            self._sender_oid, Execode.AR_ADD, AutoReplyModuleExecodeModel,
            Keyword=AutoReplyContentModel(Content=self._keyword, ContentType=self._keyword_type),
            Responses=self._responses, Pinned=self._pinned, Private=self._pinned, TagIds=self._tags,
            CooldownSec=self._cooldown)

    def is_success(self) -> bool:
        try:
            return super().is_success() and self._result.success
        except AttributeError:
            return False
