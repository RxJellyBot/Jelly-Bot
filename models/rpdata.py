from models import Model, ModelDefaultValueExt
from models.field import DictionaryField, ArrayField


class PendingRepairDataModel(Model):
    Data = DictionaryField("d", default=ModelDefaultValueExt.Required, allow_none=False)
    MissingKeys = ArrayField("m", elem_type=str, default=ModelDefaultValueExt.Required, allow_none=False)
