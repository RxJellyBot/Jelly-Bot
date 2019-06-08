from django.http import QueryDict

from ._base import BaseApiResponse


# TODO: Token Action - Auto Reply Add API Response not completed.
class AutoReplyAddResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)

    def process_ifnoerror(self):
        pass

    def is_success(self) -> bool:
        pass

    def pre_process(self):
        pass

    def serialize_success(self) -> dict:
        pass

    def serialize_failed(self) -> dict:
        pass
