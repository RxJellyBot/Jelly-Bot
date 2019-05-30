from ._base import BaseApiResponse

class AutoReplyAddResponse(BaseApiResponse):
    def is_success(self) -> bool:
        pass

    def pre_process(self):
        pass

    def serialize_success(self) -> dict:
        pass

    def serialize_failed(self) -> dict:
        pass