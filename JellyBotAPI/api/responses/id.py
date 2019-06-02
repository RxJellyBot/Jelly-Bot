from django.http import QueryDict

from ._base import BaseApiResponse


class ChannelDataQueryResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)


    def is_success(self) -> bool:
        pass

    def pre_process(self):
        pass

    def serialize_success(self) -> dict:
        pass

    def serialize_failed(self) -> dict:
        pass
