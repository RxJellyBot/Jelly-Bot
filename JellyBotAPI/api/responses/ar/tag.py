from JellyBotAPI.api.static import param, result
from JellyBotAPI.api.responses.mixin import SerializeResultOnSuccessMixin
from JellyBotAPI.api.responses import BaseApiResponse
from JellyBotAPI.SystemConfig import DataQuery

from mongodb.factory import AutoReplyManager


class AutoReplyTagPopularityResponse(SerializeResultOnSuccessMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

        self._flag[result.DataQuery.COUNT] = \
            self._count = \
            param_dict.get(param.DataQuery.COUNT, DataQuery.TagPopularitySearchCount)
        self._flag[result.DataQuery.KEYWORD] = \
            self._keyword = \
            param_dict.get(param.DataQuery.KEYWORD)

    def pre_process(self):
        super().pre_process()

    def pass_condition(self) -> bool:
        return super().pass_condition()

    def serialize_failed(self) -> dict:
        return dict()

    def serialize_extra(self) -> dict:
        return {result.FLAGS: self._flag}

    def process_pass(self):
        self._result = AutoReplyManager.get_popularity_scores(self._keyword, self._count)
