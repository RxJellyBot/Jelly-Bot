from bson import ObjectId

from extutils.locales import default_locale
from flags import ModelValidityCheckResult

from ._base import Model, ModelDefaultValueExt
from .field import PlatformField, TextField, ArrayField, ObjectIDField, ModelField


class RootUserConfigModel(Model):
    WITH_OID = False

    Locale = TextField("l", default=default_locale.pytz_code, allow_none=False)
    Name = TextField("n", allow_none=False)


class RootUserModel(Model):
    OnPlatOids = ArrayField("op", ObjectId, default=ModelDefaultValueExt.Optional, allow_none=True)
    ApiOid = ObjectIDField("api", default=ModelDefaultValueExt.Optional, allow_none=True)
    Config = ModelField("c", RootUserConfigModel)

    def perform_validity_check(self) -> ModelValidityCheckResult:
        all_empty = self.is_field_none("OnPlatOids") and self.is_field_none("ApiOid")

        if all_empty:
            return ModelValidityCheckResult.X_RTU_ALL_NONE
        else:
            return ModelValidityCheckResult.O_OK


class APIUserModel(Model):
    API_TOKEN_LENGTH = 32

    Email = TextField("e", default=ModelDefaultValueExt.Required, regex=r"^\w+@\w+",
                      allow_none=False, must_have_content=True)
    GoogleUid = TextField("goo_id", default=ModelDefaultValueExt.Required, regex=r"\w+",
                          allow_none=False, must_have_content=True)
    Token = TextField("t", default=ModelDefaultValueExt.Required, regex=rf"^\w{{{API_TOKEN_LENGTH}}}",
                      allow_none=False, must_have_content=True)


class OnPlatformUserModel(Model):
    Token = TextField("t", default=ModelDefaultValueExt.Required, allow_none=False, must_have_content=True)
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)
