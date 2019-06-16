import secrets

from ._base import BaseCollection


class GenerateTokenMixin(BaseCollection):
    token_length: int = None
    token_key: str = None

    @classmethod
    def get_token_length(cls) -> int:
        if cls.token_length is None:
            raise AttributeError(f"Assign a value to `token_length` in {cls.__name__}.")
        else:
            return cls.token_length

    @classmethod
    def get_token_key(cls) -> str:
        if cls.token_key is None:
            raise AttributeError(f"Assign a value to `token_key` in {cls.__name__}.")
        else:
            return cls.token_key

    # noinspection PyTypeChecker
    def generate_hex_token(self):
        token = secrets.token_hex(int(self.__class__.get_token_length() / 2))
        if self.count_documents({self.__class__.get_token_key(): token}) > 0:
            token = self.generate_hex_token()

        return token
