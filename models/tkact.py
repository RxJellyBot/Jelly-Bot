from models import Model
from models.field import TextField, TokenActionField, DateTimeField, DictionaryField


class TokenActionModel(Model):
    Token = "tk"
    ActionType = "a"
    Timestamp = "t"
    Data = "d"

    TOKEN_LENGTH = 10

    def _init_fields_(self, **kwargs):
        self.token = TextField(TokenActionModel.Token, regex=fr"\w{{{TokenActionModel.TOKEN_LENGTH}}}",
                               must_have_content=True)
        self.action = TokenActionField(TokenActionModel.ActionType)
        self.timestamp = DateTimeField(TokenActionModel.Timestamp)
        self.data = DictionaryField(TokenActionModel.Data)
