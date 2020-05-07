from typing import Optional

from bson import ObjectId
from cachetools import TTLCache

from models.exceptions import KeyNotExistedError
from extutils.locales import default_locale, default_language, LocaleInfo
from JellyBot.systemconfig import DataQuery
from flags import ModelValidityCheckResult, Platform

from ._base import Model
from .field import PlatformField, TextField, ArrayField, ObjectIDField, ModelField, ModelDefaultValueExt


class RootUserConfigModel(Model):
    WITH_OID = False

    Locale = TextField("l", default=default_locale.pytz_code, allow_none=False)
    Language = TextField("lg", default=default_language.code, allow_none=False)
    Name = TextField("n", allow_none=False)

    @property
    def tzinfo(self):
        return LocaleInfo.get_tzinfo(self.locale)


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

    Email = TextField("e", default=ModelDefaultValueExt.Required, regex=r"^.+@.+",
                      allow_none=False, must_have_content=True)
    GoogleUid = TextField("goo_id", default=ModelDefaultValueExt.Required, regex=r"\w+",
                          allow_none=False, must_have_content=True)
    Token = TextField("t", default=ModelDefaultValueExt.Required, regex=rf"^\w{{{API_TOKEN_LENGTH}}}",
                      allow_none=False, must_have_content=True)


_user_name_cache_ = TTLCache(maxsize=DataQuery.UserNameCacheSize, ttl=DataQuery.UserNameExpirationSeconds)


def set_uname_cache(onplat_oid: ObjectId, name: str):
    _user_name_cache_[onplat_oid] = name


class OnPlatformUserModel(Model):
    Token = TextField("t", default=ModelDefaultValueExt.Required, allow_none=False, must_have_content=True)
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)

    def get_name(self, channel_data=None) -> Optional[str]:
        if self.id not in _user_name_cache_:
            n = None

            if self.platform == Platform.LINE:
                from extline import LineApiWrapper
                from models import ChannelCollectionModel

                if isinstance(channel_data, ChannelCollectionModel):
                    raise ValueError("Finding the user name with `ChannelCollectionModel` currently not yet supported. "
                                     "Check issue #38.")

                if channel_data:
                    n = LineApiWrapper.get_user_name_safe(self.token, channel_data)
                else:
                    n = LineApiWrapper.get_user_name_safe(self.token)
            elif self.platform == Platform.DISCORD:
                from extdiscord import DiscordClientWrapper

                n = DiscordClientWrapper.get_user_name_safe(self.token)

            if n:
                set_uname_cache(self.id, n)
            else:
                # Mark unavailable
                from mongodb.factory import ProfileManager, RootUserManager

                root_data_result = RootUserManager.get_root_data_onplat(self.platform, self.token, auto_register=False)
                if root_data_result.success:
                    ProfileManager.mark_unavailable_async(channel_data.id, root_data_result.model.id)

        return _user_name_cache_.get(self.id)

    def get_name_str(self, channel_data=None) -> str:
        n = self.get_name(channel_data)

        if n:
            return n
        else:
            return f"{self.token} ({self.platform.key})"
