from datetime import timedelta, datetime
from typing import Optional

from extutils.dt import localtime
from JellyBot import systemconfig
from flags import ModelValidityCheckResult, Execode
from models import Model, ModelDefaultValueExt, AutoReplyModuleExecodeModel
from models.exceptions import ModelConstructionError
from models.field import TextField, ExecodeField, DateTimeField, DictionaryField, ObjectIDField


class ExecodeEntryModel(Model):
    EXECODE_LENGTH = 10

    CreatorOid = ObjectIDField("cr", default=ModelDefaultValueExt.Required, stores_uid=True)
    Execode = TextField("tk", default=ModelDefaultValueExt.Required,
                        regex=fr"\w{{{EXECODE_LENGTH}}}", must_have_content=True)
    ActionType = ExecodeField("a", default=ModelDefaultValueExt.Required)
    Timestamp = DateTimeField("t", default=ModelDefaultValueExt.Required)
    Data = DictionaryField("d")

    @property
    def expire_time(self) -> Optional[datetime]:
        return localtime(self.timestamp) + timedelta(seconds=systemconfig.Database.ExecodeExpirySeconds)

    def perform_validity_check(self) -> ModelValidityCheckResult:
        if self.action_type == Execode.UNKNOWN:
            return ModelValidityCheckResult.X_EXC_ACTION_UNKNOWN
        elif self.action_type == Execode.AR_ADD:
            try:
                AutoReplyModuleExecodeModel(**self.data, from_db=True)
            except ModelConstructionError:
                return ModelValidityCheckResult.X_EXC_DATA_ERROR
            except Exception:
                return ModelValidityCheckResult.X_ERROR

        return ModelValidityCheckResult.O_OK
