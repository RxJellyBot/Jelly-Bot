from JellyBot.api.responses import BaseApiResponse
from JellyBot.api.static import param
from JellyBot.api.responses.mixin import SerializeResultExtraMixin, RequireSenderMixin
from mongodb.factory import ShortUrlDataManager


class ShortUrlShortenResponse(SerializeResultExtraMixin, RequireSenderMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

        self._param_dict.update(**{
            param.Service.ShortUrl.TARGET: param_dict.get(param.Service.ShortUrl.TARGET)
        })

        self._target = self._param_dict[param.Service.ShortUrl.TARGET]

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._result.success

    def pre_process(self):
        return super().pre_process()

    def serialize_success(self) -> dict:
        return super().serialize_success()

    def serialize_failed(self) -> dict:
        return super().serialize_failed()

    def process_pass(self):
        self._result = ShortUrlDataManager.create_record(self._target, self._sender_oid)

    @property
    def param_dict(self) -> dict:
        return self._param_dict


class ShortUrlTargetChangeResponse(SerializeResultExtraMixin, RequireSenderMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

        self._param_dict.update(**{
            param.Service.ShortUrl.CODE: param_dict.get(param.Service.ShortUrl.CODE),
            param.Service.ShortUrl.TARGET: param_dict.get(param.Service.ShortUrl.TARGET)
        })

        self._code = self._param_dict[param.Service.ShortUrl.CODE]
        self._target = self._param_dict[param.Service.ShortUrl.TARGET]

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._result

    def pre_process(self):
        return super().pre_process()

    def serialize_success(self) -> dict:
        return super().serialize_success()

    def serialize_failed(self) -> dict:
        return super().serialize_failed()

    def process_pass(self):
        self._result = ShortUrlDataManager.update_target(self._sender_oid, self._target)

    @property
    def param_dict(self) -> dict:
        return self._param_dict
