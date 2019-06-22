from models import Model, ModelDefaultValueExt
from models.field import DictionaryField


class PendingRepairDataModel(Model):
    Data = DictionaryField("d", default=ModelDefaultValueExt.Required, allow_none=False)
    MissingKeys = DictionaryField("m", default=ModelDefaultValueExt.Required, allow_none=False)
