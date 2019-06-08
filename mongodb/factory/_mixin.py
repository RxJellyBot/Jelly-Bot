import secrets

from extutils.decorators import abstractproperty
from ._base import BaseCollection


class GenerateTokenMixin(BaseCollection):
    @abstractproperty
    def token_length(self) -> int:
        raise AttributeError(f"Assign a value to `token_length` in {self.__class__.__name__}.")

    @abstractproperty
    def token_key(self) -> str:
        raise AttributeError(f"Assign a value to `token_key` in {self.__class__.__name__}.")

    # noinspection PyTypeChecker
    def generate_hex_token(self):
        token = secrets.token_hex(int(self.__class__.token_length / 2))
        if self.count_documents({self.__class__.token_key: token}) > 0:
            token = self.generate_hex_token()

        return token
