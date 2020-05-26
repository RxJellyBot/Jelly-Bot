import secrets

from pymongo.collection import Collection


class GenerateTokenMixin(Collection):
    token_length: int = None
    token_key: str = None

    @classmethod
    def get_token_length(cls) -> int:
        if cls.token_length is None:
            raise AttributeError(f"Specify the desired token length to `token_length` in {cls.__qualname__}.")
        else:
            return cls.token_length

    @classmethod
    def get_token_key(cls) -> str:
        if cls.token_key is None:
            raise AttributeError(f"Specify the json key of the token to `token_key` in {cls.__qualname__}.")
        else:
            return cls.token_key

    @classmethod
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)

        # Calling both `get` methods to check if the class variable has been defined.
        cls.get_token_length()
        cls.get_token_key()

        return obj

    def generate_hex_token(self):
        token = secrets.token_hex(self.get_token_length() // 2 + 1)[:self.get_token_length()]
        if self.count_documents({self.get_token_key(): token}) > 0:
            token = self.generate_hex_token()

        return token
