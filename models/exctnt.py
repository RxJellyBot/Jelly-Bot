from models.field import (
    ExtraContentTypeField, TextField, DateTimeField
)


from ._base import Model, ModelDefaultValueExt


class ExtraContentModel(Model):
    Type = ExtraContentTypeField("t")
    Content = TextField("c", default=ModelDefaultValueExt.Required)
    ExpireTime = DateTimeField("e", default=ModelDefaultValueExt.Required)
