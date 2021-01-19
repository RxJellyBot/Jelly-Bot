"""
Model of user-identity-related data.

User will have an identity data recording their platform-specific identity.
This data will then being connected to the main user data (:class:`RootUserModel`).

For example, if a user access the bot via LINE, they will have an :class:`OnPlatformUserModel` recording their token
and another main user data connects that :class:`OnPlatformUserModel`.

Besides any user identity or platform-specific controls, all accesses should
use the ID of :class:`RootUserModel` as UID.
"""
from typing import Optional

from bson import ObjectId
from cachetools import TTLCache

from models.exceptions import FieldKeyNotExistError
from extutils.locales import DEFAULT_LOCALE, DEFAULT_LANGUAGE, LocaleInfo
from JellyBot.systemconfig import DataQuery
from flags import ModelValidityCheckResult, Platform

from ._base import Model
from .field import PlatformField, TextField, ArrayField, ObjectIDField, ModelField, ModelDefaultValueExt


class RootUserConfigModel(Model):
    """
    User config model.

    This should be placed in the field ``Config`` of :class:`RootUserModel`.
    """

    WITH_OID = False

    Locale = TextField("l", default=DEFAULT_LOCALE.pytz_code, allow_none=False)
    Language = TextField("lg", default=DEFAULT_LANGUAGE.code, allow_none=False)
    Name = TextField("n", allow_none=False)

    @property
    def pytz_code(self) -> str:
        """
        Get the IANA timezone identifier of this config. If the locale is invalid / not found, return the default one.

        :return: IANA timezone identifier of this config
        """
        tzinfo = self.tzinfo
        if not tzinfo:
            return DEFAULT_LOCALE.pytz_code

        return tzinfo.tzidentifier

    @property
    def tzinfo(self):
        """
        Get the :class:`tzinfo` of this config.

        :return: `tzinfo` of this config
        """
        return LocaleInfo.get_tzinfo(self.locale, silent_fail=True)


class RootUserModel(Model):
    """
    Main user identity model.

    This connects various types of platform identities as one.
    """

    OnPlatOids = ArrayField("op", ObjectId, default=ModelDefaultValueExt.Optional, allow_none=True)
    ApiOid = ObjectIDField("api", default=ModelDefaultValueExt.Optional, allow_none=True)
    Config = ModelField("c", RootUserConfigModel)

    def perform_validity_check(self) -> ModelValidityCheckResult:
        all_empty = not self.has_onplat_data and not self.has_api_data

        if all_empty:
            return ModelValidityCheckResult.X_RTU_ALL_NONE

        return ModelValidityCheckResult.O_OK

    @property
    def has_onplat_data(self) -> bool:
        """
        Check if there is any on-platform identity connected to this data.

        :return: if there is any on-platform identity connected to this data
        """
        try:
            return not self.is_field_none("OnPlatOids")
        except (KeyError, FieldKeyNotExistError, AttributeError):
            return False

    @property
    def has_api_data(self) -> bool:
        """
        Check if there is any website identity connected to this data.

        :return: if there is any website identity connected to this data
        """
        try:
            return not self.is_field_none("ApiOid")
        except (KeyError, FieldKeyNotExistError, AttributeError):
            return False


class APIUserModel(Model):
    """Website user identity model."""

    API_TOKEN_LENGTH = 32

    Email = TextField("e", default=ModelDefaultValueExt.Required, regex=r"^.+@.+",
                      allow_none=False, must_have_content=True)
    GoogleUid = TextField("goo_id", default=ModelDefaultValueExt.Required, regex=r"\w+",
                          allow_none=False, must_have_content=True)
    Token = TextField("t", default=ModelDefaultValueExt.Required, regex=rf"^\w{{{API_TOKEN_LENGTH}}}",
                      allow_none=False, must_have_content=True)


_user_name_cache_ = TTLCache(maxsize=DataQuery.UserNameCacheSize, ttl=DataQuery.UserNameExpirationSeconds)


def set_uname_cache(onplat_oid: ObjectId, name: str):
    """
    Set the user name ``name`` of ``onplat_oid`` to the cache.

    The cache data will expire the data once the size reaches ``DataQuery.UserNameCacheSize`` or
    ``DataQuery.UserNameExpirationSeconds`` seconds passed from the time the name was being stored.

    :param onplat_oid: OID of the on-platform identity (not the root OID)
    :param name: name of the user
    """
    _user_name_cache_[onplat_oid] = name


def clear_uname_cache():
    """Clear the user name cache."""
    _user_name_cache_.clear()


class OnPlatformUserModel(Model):
    """
    Model of the on-platform identity.

    ``Token`` should be an identifier that can uniquely identifies a user.
    """

    Token = TextField("t", default=ModelDefaultValueExt.Required, allow_none=False, must_have_content=True)
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)

    def get_name(self, channel_model=None) -> Optional[str]:
        """
        Get the user name. Returns ``None`` if unavailable.

        Also stores the user name to cache if available.

        .. note::
            According to the API spec of LINE, if the user did not add the bot as their friend, the bot will not be
            able to get the user name. So if the identity platform is :class:`Platform.LINE`, provide
            ``channel_model`` will have a better chance to get the user name.

        :param channel_model: channel data to get the user name
        :return: user name if found, `None` otherwise
        """
        # Checking `get_oid()` because the model might be constructed in the code (no ID) and
        # call `get_name()` afterward without storing it to the database
        if not self.get_oid() or self.id in _user_name_cache_:
            return _user_name_cache_.get(self.id)

        name = None

        # Get the user name according to the platform
        # There will be some inline imports to prevent circular import

        # pylint: disable=import-outside-toplevel

        if self.platform == Platform.LINE:
            from extline import LineApiWrapper
            from models import ChannelCollectionModel

            if isinstance(channel_model, ChannelCollectionModel):
                raise ValueError("Finding the user name with `ChannelCollectionModel` which is "
                                 "currently not yet supported. Check issue #38.")

            name = LineApiWrapper.get_user_name_safe(self.token, channel_model=channel_model)
        elif self.platform == Platform.DISCORD:
            from extdiscord.core import DiscordClientWrapper

            name = DiscordClientWrapper.get_user_name_safe(self.token)

        if name:
            set_uname_cache(self.id, name)
        elif channel_model.platform == self.platform:
            # If the channel platform and the data platform is the same, check for the availability
            from mongodb.factory import ProfileManager, RootUserManager

            root_data_result = RootUserManager.get_root_data_onplat(self.platform, self.token, auto_register=False)
            if root_data_result.success:
                ProfileManager.mark_unavailable_async(channel_model.id, root_data_result.model.id)

        # pylint: enable=import-outside-toplevel

        return name

    def get_name_str(self, channel_model=None) -> str:
        """
        Get the user name by calling ``get_name()``. Returns ``<TOKEN> (<PLATFORM>)`` if unavailable.

        :param channel_model: channel data to get the user name
        :return: user name if found, `<TOKEN> (<PLATFORM>)` otherwise
        """
        name = self.get_name(channel_model)

        if not name:
            return f"{self.token} ({self.platform.key})"

        return name

    @staticmethod
    def clear_name_cache():
        """Clear the user name cache."""
        clear_uname_cache()
