from abc import ABC

from JellyBotAPI import SystemConfig
from JellyBotAPI.api.static import result, info, param
from JellyBotAPI.api.responses import BaseApiResponse
from JellyBotAPI.api.responses.mixin import (
    HandleChannelOidMixin, SerializeErrorMixin, RequireSenderMixin, SerializeResultExtraMixin
)
from extutils import cast_keep_none
from flags import AutoReplyContentType, TokenAction
from models import AutoReplyModuleModel, AutoReplyModuleTokenActionModel
from mongodb.factory import (
    AutoReplyManager, AutoReplyContentManager, TokenActionManager
)


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
        r = AutoReplyContentManager.get_content(self._keyword, self._keyword_type)
        if r.success:
            self._keyword = self._data[k] = r.model.id
        else:
            self._err[k] = r.serialize()

    def _handle_keyword_type_(self):
        self._keyword_type = int(AutoReplyContentType.default() or self._keyword_type)

    def _handle_responses_(self):
        k = result.AutoReplyResponse.RESPONSES
        resp_err = list()
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

            if r.success:
                resp_list.append(r.model.id)
            else:
                resp_err.append(r.serialize())

        if len(resp_err) > 0:
            self._err[k] = resp_err
        else:
            self._responses = self._data[k] = resp_list

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
            tags = self._tags.split(SystemConfig.AutoReply.TAG_SPLITTOR)
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

    def is_success(self) -> bool:
        try:
            return super().is_success() and self._result.success
        except AttributeError:
            return False

    @property
    def param_dict(self) -> dict:
        return self._param_dict


class AutoReplyAddResponse(HandleChannelOidMixin, AutoReplyAddBaseResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

    def pre_process(self):
        super().pre_process()

    def process_pass(self):
        self._result = AutoReplyManager.add_conn(
            self._keyword, self._responses, self._sender_oid, self.get_channel_oid(),
            self._pinned, self._private, self._tags, self._cooldown)


class AutoReplyAddTokenActionResponse(AutoReplyAddBaseResponse):
    def process_pass(self):
        self._result = TokenActionManager.enqueue_action(
            self._sender_oid, TokenAction.AR_ADD, AutoReplyModuleTokenActionModel,
            KeywordOid=self._keyword, ResponsesOids=self._responses, CreatorOid=self._sender_oid,
            Pinned=self._pinned, Private=self._pinned, TagIds=self._tags, CooldownSec=self._cooldown)
