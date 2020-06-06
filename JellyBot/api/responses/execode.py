from flags import Execode
from JellyBot.api.static import param, result
from JellyBot.api.responses.mixin import (
    SerializeErrorMixin, SerializeResultOnSuccessMixin, RequireSenderMixin, SerializeResultExtraMixin
)
from mongodb.factory import ExecodeManager

from ._base import BaseApiResponse


class ExecodeCompleteApiResponse(SerializeErrorMixin, SerializeResultExtraMixin, BaseApiResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._execode = param_dict.get(param.Execode.EXECODE)
        self._action_type = param_dict.get(param.Execode.ACTION_TYPE_ID)
        self._param_dict.update(**param_dict)
        self._param_dict[param.Execode.USER_OID] = sender_oid

    def pass_condition(self) -> bool:
        return self._execode and self._result.success

    def _handle_execode(self):
        if not self._execode:
            self._err[result.ExecodeResponse.EXECODE] = self._execode

    def _handle_action_type(self):
        if self._action_type:
            self._action_type = Execode.cast(self._action_type)

    def pre_process(self):
        self._handle_execode()
        self._handle_action_type()
        self._result = ExecodeManager.complete_execode(self._execode, self.param_dict, action=self._action_type)

    def process_pass(self):
        pass

    def serialize_success(self) -> dict:
        return dict()


class ExecodeListApiResponse(
        RequireSenderMixin, SerializeErrorMixin, SerializeResultOnSuccessMixin, BaseApiResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

    def process_pass(self):
        self._result = list(ExecodeManager.get_queued_execodes(self._sender_oid))

    def pre_process(self):
        super().pre_process()
