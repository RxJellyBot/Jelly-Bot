from datetime import timedelta

from JellyBot.sysconfig import Database
from models.field import (
    ExtraContentTypeField, TextField, DateTimeField
)


from ._base import Model, ModelDefaultValueExt


class ExtraContentModel(Model):
    Type = ExtraContentTypeField("tp")
    Title = TextField("t", default=ModelDefaultValueExt.Optional)
    Content = TextField("c", default=ModelDefaultValueExt.Required)
    Timestamp = DateTimeField("e", default=ModelDefaultValueExt.Required)
    
    @property
    def expires_on(self):
        return self.timestamp + timedelta(seconds=Database.ExtraContentExpirySeconds)
