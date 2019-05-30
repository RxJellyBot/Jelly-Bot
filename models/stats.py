from models.field import BooleanField, DictionaryField, APIActionTypeField, DateTimeField, TextField
from models import Model


class APIStatisticModel(Model):
    Timestamp = "t"
    APIAction = "a"
    Parameter = "p"
    Response = "r"
    Success = "s"
    PathInfo = "pi"
    PathInfoFull = "pf"

    def _init_fields_(self, **kwargs):
        self.timestamp = DateTimeField(APIStatisticModel.Timestamp, allow_none=False)
        self.api_action = APIActionTypeField(APIStatisticModel.APIAction, allow_none=False)
        self.parameter = DictionaryField(APIStatisticModel.Parameter, allow_none=True)
        self.response = DictionaryField(APIStatisticModel.Response, allow_none=True)
        self.success = BooleanField(APIStatisticModel.Success, allow_none=True)
        self.path_info = TextField(APIStatisticModel.PathInfo, allow_none=False)
        self.path_info_full = TextField(APIStatisticModel.PathInfoFull, allow_none=False)
