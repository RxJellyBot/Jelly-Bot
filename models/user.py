from threading import Thread

from bson import ObjectId
from cachetools import TTLCache

from models.exceptions import KeyNotExistedError
from extutils.locales import default_locale, default_language, LocaleInfo
from JellyBot.systemconfig import DataQuery
from flags import ModelValidityCheckResult, Platform

from ._base import Model, ModelDefaultValueExt
from .field import PlatformField, TextField, ArrayField, ObjectIDField, ModelField


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

    Email = TextField("e", default=ModelDefaultValueExt.Required, regex=r"^\w+@\w+",
                      allow_none=False, must_have_content=True)
    GoogleUid = TextField("goo_id", default=ModelDefaultValueExt.Required, regex=r"\w+",
                          allow_none=False, must_have_content=True)
    Token = TextField("t", default=ModelDefaultValueExt.Required, regex=rf"^\w{{{API_TOKEN_LENGTH}}}",
                      allow_none=False, must_have_content=True)


_user_name_cache_ = TTLCache(maxsize=DataQuery.UserNameCacheSize, ttl=DataQuery.UserNameExpirationSeconds)


def load_user_name_cache():
    def fn():
        from mongodb.factory import RootUserManager, ProfileManager, ChannelManager

        dict_onplat = RootUserManager.get_onplat_data_dict()
        dict_to_root = RootUserManager.get_onplat_to_root_dict()
        dict_user_channel = ProfileManager.get_users_exist_channel_dict(list(dict_to_root.values()))
        all_cid = set()
        for cid_set in dict_user_channel.values():
            all_cid.update(cid_set)
        dict_channel = ChannelManager.get_channel_dict(list(all_cid))

        for onplat_oid, onplat_data in dict_onplat.items():
            root_oid = dict_to_root.get(onplat_oid)
            if not root_oid:
                continue

            channel_set = dict_user_channel.get(root_oid)
            if not channel_set:
                continue

            channel_id = channel_set.pop()
            if not channel_id:
                continue

            channel_model = dict_channel.get(channel_id)
            if not channel_model:
                continue

            _user_name_cache_[onplat_oid] = onplat_data.get_name(channel_model, mark_x_on_not_found=False)

    Thread(target=fn).start()


class OnPlatformUserModel(Model):
    Token = TextField("t", default=ModelDefaultValueExt.Required, allow_none=False, must_have_content=True)
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)

    def get_name(self, channel_data=None, mark_x_on_not_found=True) -> str:
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
            elif mark_x_on_not_found:
                # Mark unavailable
                from mongodb.factory import ProfileManager, RootUserManager

                root_data_result = RootUserManager.get_root_data_onplat(self.platform, self.token, auto_register=False)
                if root_data_result.success:
                    ProfileManager.mark_unavailable_async(channel_data.id, root_data_result.model.id)

        return _user_name_cache_.get(self.id, f"{self.token} ({self.platform.key})")
