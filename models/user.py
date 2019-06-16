from bson import ObjectId

from extutils.locales import default_locale

from ._base import Model, ModelDefaultValueExtension
from ._mixin import CreateDefaultMixin
from .exceptions import InvalidModelError
from .field import PlatformField, TextField, ArrayField, ObjectIDField, ModelField


class RootUserConfigModel(CreateDefaultMixin, Model):
    Locale = "l"
    Name = "n"

    default_vals = (
        (Locale, default_locale.pytz_code),
        (Name, ModelDefaultValueExtension.Required),
    )

    def _init_fields_(self, **kwargs):
        self.locale = TextField(RootUserConfigModel.Locale, allow_none=False)
        self.name = TextField(RootUserConfigModel.Name, allow_none=False)


class RootUserModel(Model):
    APIUserID = "api"
    OnPlatformUserIDs = "op"
    Config = "c"

    default_vals = (
        (APIUserID, ModelDefaultValueExtension.Optional),
        (OnPlatformUserIDs, ModelDefaultValueExtension.Optional),
        (Config, RootUserConfigModel.create_default().serialize())
    )

    dict_models = (
        (Config, RootUserConfigModel),
    )

    def _init_fields_(self, **kwargs):
        self.onplat_oids = ArrayField(RootUserModel.OnPlatformUserIDs, ObjectId, allow_none=True)
        self.api_oid = ObjectIDField(RootUserModel.APIUserID, allow_none=True)
        self.config = ModelField(RootUserModel.Config, RootUserConfigModel)

    def is_valid(self):
        return (not self.onplat_oids.is_none()) or (not self.api_oid.is_none())

    def handle_invalid(self):
        raise InvalidModelError(self.__class__.__name__,
                                "Either onPlatformIDs or APIoid need(s) to have value(s).")


class APIUserModel(Model):
    Email = "e"
    GoogleUniqueID = "goo_id"
    APIToken = "t"

    default_vals = (
        (Email, ModelDefaultValueExtension.Required),
        (GoogleUniqueID, ModelDefaultValueExtension.Required),
        (APIToken, ModelDefaultValueExtension.Required)
    )

    API_TOKEN_LENGTH = 32

    def _init_fields_(self, **kwargs):
        self.email = TextField(APIUserModel.Email, regex=r"^\w+@\w+", allow_none=False)
        self.gid_id = TextField(APIUserModel.GoogleUniqueID, regex=r"\w+", allow_none=False, must_have_content=True)
        self.token = TextField(APIUserModel.APIToken,
                               regex=rf"^\w{{{APIUserModel.API_TOKEN_LENGTH}}}", allow_none=False)


class OnPlatformUserModel(Model):
    UserToken = "t"
    Platform = "p"

    default_vals = (
        (UserToken, ModelDefaultValueExtension.Required),
        (Platform, ModelDefaultValueExtension.Required)
    )

    def _init_fields_(self, **kwargs):
        self.token = TextField(OnPlatformUserModel.UserToken)
        self.platform = PlatformField(OnPlatformUserModel.Platform)
