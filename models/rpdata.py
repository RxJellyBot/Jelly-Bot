from models import Model, ModelDefaultValueExtension
from models.field import DictionaryField


class PendingRepairDataModel(Model):
    Data = "d"
    MissingKeys = "m"

    default_vals = (
        (Data, ModelDefaultValueExtension.Required),
        (MissingKeys, ModelDefaultValueExtension.Required),
    )

    def _init_fields_(self, **kwargs):
        self.data = DictionaryField(PendingRepairDataModel.Data, allow_none=False)
        self.missing_keys = DictionaryField(PendingRepairDataModel.MissingKeys, allow_none=False)
