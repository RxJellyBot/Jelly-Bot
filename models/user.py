from bson import ObjectId
from cachetools import TTLCache

from models.exceptions import KeyNotExistedError
from extutils.locales import default_locale, default_language
from JellyBot.systemconfig import DataQuery
from flags import ModelValidityCheckResult, Platform

from ._base import Model, ModelDefaultValueExt
from .field import PlatformField, TextField, ArrayField, ObjectIDField, ModelField


class RootUserConfigModel(Model):
    WITH_OID = False

    Locale = TextField("l", default=default_locale.pytz_code, allow_none=False)
    Language = TextField("lg", default=default_language.code, allow_none=False)
    Name = TextField("n", allow_none=False)


class RootUserModel(Model):
    OnPlatOids = ArrayField("op", ObjectId, default=ModelDefaultValueExt.Optional, allow_none=True)
    ApiOid = ObjectIDField("api", default=ModelDefaultValueExt.Optional, allow_none=True)
    Config = ModelField("c", RootUserConfigModel)

    def perform_validity_check(self) -> ModelValidityCheckResult:
        all_empty = not self.has_onplat_data and not self.has_api_data

        if all_empty:
            return ModelValidityCheckResult.X_RTU_ALL_NONE
        else:
            return ModelValidityCheckResult.O_OK

    @property
    def has_onplat_data(self) -> bool:
        try:
            return not self.is_field_none("OnPlatOids")
        except (KeyError, KeyNotExistedError, AttributeError):
            return False

    @property
    def has_api_data(self) -> bool:
        try:
            return not self.is_field_none("ApiOid")
        except (KeyError, KeyNotExistedError, AttributeError):
            return False


class APIUserModel(Model):
    API_TOKEN_LENGTH = 32

    Email = TextField("e", default=ModelDefaultValueExt.Required, regex=r"^\w+@\w+",
                      allow_none=False, must_have_content=True)
    GoogleUid = TextField("goo_id", default=ModelDefaultValueExt.Required, regex=r"\w+",
                          allow_none=False, must_have_content=True)
    Token = TextField("t", default=ModelDefaultValueExt.Required, regex=rf"^\w{{{API_TOKEN_LENGTH}}}",
                      allow_none=False, must_have_content=True)


_user_name_cache_ = TTLCache(maxsize=DataQuery.UserNameCacheSize, ttl=DataQuery.UserNameExpirationSeconds)


class OnPlatformUserModel(Model):
    Token = TextField("t", default=ModelDefaultValueExt.Required, allow_none=False, must_have_content=True)
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)

    def get_name(self, channel_data=None) -> str:
        if self.id not in _user_name_cache_:
            n = None

            if self.platform == Platform.LINE:
                from extline import LineApiWrapper

                if channel_data:
                    n = LineApiWrapper.get_user_name_safe(self.token, channel_data)
                else:
                    n = LineApiWrapper.get_user_name_safe(self.token)
            elif self.platform == Platform.DISCORD:
                from extdiscord import DiscordClientWrapper

                n = DiscordClientWrapper.get_user_name_safe(self.token)

            if n:
                _user_name_cache_[self.id] = n

        return _user_name_cache_.get(self.id, f"{self.token} ({self.platform.key})")
