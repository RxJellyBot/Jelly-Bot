"""Data managers of the user identities."""
from collections import namedtuple
from datetime import tzinfo
from typing import Optional, Dict, List, Union, NamedTuple

from bson import ObjectId

from pymongo import ReturnDocument

from extutils.gidentity import GoogleIdentityUserData
from extutils.emailutils import MailSender
from extutils.locales import DEFAULT_LOCALE
from extutils.checker import arg_type_ensure
from flags import Platform
from models import APIUserModel, OnPlatformUserModel, RootUserModel, RootUserConfigModel, OID_KEY, ChannelModel, \
    ChannelCollectionModel
from mongodb.factory.results import OperationOutcome

from ._base import BaseCollection
from .mixin import GenerateTokenMixin
from .results import (
    WriteOutcome, GetOutcome, UpdateOutcome,
    APIUserRegistrationResult, OnPlatformUserRegistrationResult, RootUserRegistrationResult,
    RootUserUpdateResult, GetRootUserDataResult
)

__all__ = ("APIUserManager", "OnPlatformIdentityManager", "RootUserManager",)

DB_NAME = "user"

UserNameEntryType = NamedTuple("UserNameEntry", [("user_id", ObjectId), ("user_name", str)])


class _APIUserManager(GenerateTokenMixin, BaseCollection):
    """Class to manage the API user identity."""

    token_length = APIUserModel.API_TOKEN_LENGTH
    token_key = APIUserModel.Token.key

    database_name = DB_NAME
    collection_name = "api"
    model_class = APIUserModel

    def build_indexes(self):
        self.create_index(APIUserModel.GoogleUid.key, unique=True, name="Google Identity Unique ID")
        self.create_index(APIUserModel.Token.key, unique=True, name="Jelly Bot API Token")

    def ensure_register(self, id_data: GoogleIdentityUserData) -> APIUserRegistrationResult:
        """
        Ensure that the user is registered by Google Identity data.

        :param id_data: Google Identity data to ensure registration
        :return: result of the registration
        """
        token = None
        model, outcome, ex = \
            self.insert_one_data(Email=id_data.email, GoogleUid=id_data.uid, Token=self.generate_hex_token())

        if outcome.is_inserted:
            token = model.token
        else:
            model = self.get_user_data_google_id(id_data.uid)
            if model is None:
                if ex is not None:
                    outcome = WriteOutcome.X_EXCEPTION_OCCURRED
                else:
                    outcome = WriteOutcome.X_NOT_FOUND_ABORTED_INSERT
            else:
                token = model.token

        return APIUserRegistrationResult(outcome, ex, model, token)

    def get_user_data_id_data(self, id_data: GoogleIdentityUserData) -> Optional[APIUserModel]:
        """
        Get the :class:`APIUserModel` by Google Identity data.

        :param id_data: Google Identity data to get the user data
        :return: `APIUserModel` if found, `None` otherwise
        """
        return self.get_user_data_google_id(id_data.uid)

    def get_user_data_token(self, token: str) -> Optional[APIUserModel]:
        """
        Get the :class:`APIUserModel` by its API token.

        :param token: token to get the user data
        :return: `APIUserModel` if found, `None` otherwise
        """
        return self.find_one_casted({APIUserModel.Token.key: token})

    def get_user_data_google_id(self, goo_uid: str) -> Optional[APIUserModel]:
        """
        Get the :class:`APIUserModel` by its Google Identity UID.

        :param goo_uid: Google Identity UID
        :return: `APIUserModel` if found, `None` otherwise
        """
        return self.find_one_casted({APIUserModel.GoogleUid.key: goo_uid})


class _OnPlatformIdentityManager(BaseCollection):
    """Class to manage the on-platform identity."""

    database_name = DB_NAME
    collection_name = "onplat"
    model_class = OnPlatformUserModel

    def build_indexes(self):
        self.create_index([(OnPlatformUserModel.Platform.key, 1), (OnPlatformUserModel.Token.key, 1)],
                          unique=True, name="Compound - Identity")

    @arg_type_ensure
    def ensure_register(self, platform: Platform, user_token: str) -> OnPlatformUserRegistrationResult:
        """
        Ensure that the user is registered by its ``platform`` and ``user_token``.

        :param platform: platform of the user
        :param user_token: token of the user
        :return: user registration result
        """
        entry, outcome, ex = self.insert_one_data(Token=user_token, Platform=platform)

        if not outcome.is_inserted:
            entry = self.get_onplat(platform, user_token)
            if not entry:
                outcome = WriteOutcome.X_NOT_FOUND_ABORTED_INSERT

        return OnPlatformUserRegistrationResult(outcome, ex, entry)

    @arg_type_ensure
    def get_onplat(self, platform: Platform, user_token: str) -> Optional[OnPlatformUserModel]:
        """
        Get the on-platform user identity by its ``platform`` and ``user_token``.

        :param platform: platform of the user
        :param user_token: token of the user
        :return: `OnPlatformUserModel` if found, `None` otherwise
        """
        return self.find_one_casted({
            OnPlatformUserModel.Platform.key: platform, OnPlatformUserModel.Token.key: user_token
        })

    @arg_type_ensure
    def get_onplat_by_oid(self, oid: ObjectId) -> Optional[OnPlatformUserModel]:
        """
        Get the on-platform user identity by its OID.

        Note that this OID is the OID of the on-platform identity, **NOT** the OID of the root identity.

        :param oid: OID of the user
        :return: `OnPlatformUserModel` if found, `None` otherwise
        """
        return self.find_one_casted({OnPlatformUserModel.Id.key: oid})


class _RootUserManager(BaseCollection):
    """Class to manage the root user data. This also serve as the main data controller of the user identities."""

    database_name = DB_NAME
    collection_name = "root"
    model_class = RootUserModel

    def build_indexes(self):
        self.create_index(
            RootUserModel.ApiOid.key, unique=True, name="API User OID",
            partialFilterExpression={RootUserModel.ApiOid.key: {"$exists": True}})
        self.create_index(
            RootUserModel.OnPlatOids.key, unique=True, name="On Platform Identity OIDs",
            partialFilterExpression={RootUserModel.OnPlatOids.key: {"$exists": True}})

    def clear(self):
        super().clear()

        APIUserManager.clear()
        OnPlatformIdentityManager.clear()
        OnPlatformUserModel.clear_name_cache()

    def register_onplat(self, platform: Platform, user_token: str) -> RootUserRegistrationResult:
        """
        Ensure that the on-platform user is registered.

        :param platform: platform of the user
        :param user_token: token of the user
        :return: result of the user identity registration
        """
        user_reg_result = OnPlatformIdentityManager.ensure_register(platform, user_token)
        plat_oid = user_reg_result.model.id if user_reg_result.outcome.is_success else None

        if not plat_oid:
            return RootUserRegistrationResult(WriteOutcome.X_ON_REG_ONPLAT, None, None,
                                              WriteOutcome.X_NOT_EXECUTED, user_reg_result)

        model, outcome, ex = self.insert_one_data(OnPlatOids=[plat_oid])

        if not outcome.is_success:
            return RootUserRegistrationResult(WriteOutcome.X_ON_CONN_ONPLAT, ex, model, outcome, user_reg_result)

        if outcome == WriteOutcome.O_DATA_EXISTS:
            return RootUserRegistrationResult(WriteOutcome.O_DATA_EXISTS, ex, model, outcome, user_reg_result)

        return RootUserRegistrationResult(WriteOutcome.O_INSERTED, ex, model, outcome, user_reg_result)

    def register_google(self, id_data: GoogleIdentityUserData) -> RootUserRegistrationResult:
        """
        Ensure that the API user who are using Google to login is registered.

        According to the documentation, to avoid desync of the email which can be changed in the user settings on
        Google, API user (this bot) should update the email every time the user logged in. Hence this function will do
        so.

        :param id_data: Google Identity data of the user
        :return: result of the user identity registration
        """
        user_reg_result = APIUserManager.ensure_register(id_data)
        plat_oid = user_reg_result.model.id if user_reg_result.outcome.is_success else None

        if not plat_oid:
            return RootUserRegistrationResult(WriteOutcome.X_ON_REG_API, None, None,
                                              WriteOutcome.X_NOT_EXECUTED, user_reg_result)

        model, outcome, ex = self.insert_one_data(ApiOid=plat_oid)

        if not outcome.is_success:
            return RootUserRegistrationResult(WriteOutcome.X_ON_CONN_API, ex, model, outcome, user_reg_result)

        if outcome == WriteOutcome.O_DATA_EXISTS:
            # Updating the email per the documentation
            APIUserManager.update_many_async({APIUserModel.GoogleUid.key: id_data.uid,
                                              APIUserModel.Email.key: {"$ne": id_data.email}},
                                             {"$set": {APIUserModel.Email.key: id_data.email}})

            return RootUserRegistrationResult(WriteOutcome.O_DATA_EXISTS, ex, model, outcome, user_reg_result)

        return RootUserRegistrationResult(WriteOutcome.O_INSERTED, ex, model, outcome, user_reg_result)

    @arg_type_ensure
    def get_root_data_oid(self, root_oid: ObjectId) -> Optional[RootUserModel]:
        """
        Get the root user data by its OID.

        :param root_oid: OID of the user
        :return: `RootUserModel` if found, `None` otherwise
        """
        return self.find_one_casted({OID_KEY: root_oid})

    @arg_type_ensure
    def get_root_data_uname(
            self, root_oid: ObjectId, channel_data: Union[ChannelModel, ChannelCollectionModel, None] = None,
            on_not_found: Optional[str] = None) -> Optional[UserNameEntryType]:
        """
        Get the user name.

        The steps of getting the user name below:

        1. Check if the user data exists.

            - If not, returns ``None``

            - If exists, go to the next step

        2. Check if the user defined their name on the bot.

            - If defined, return it as the ``user_name`` of :class:`UserNameEntryType`

            - If not, go to the next step

        3. Check if the user has linked on-platform identity.

            - If not, return ``on_not_found`` of ``None`` (if the previous is not defined)
              as the ``user_name`` of :class:`UserNameEntryType`

            - If exists, go to the next step

        4. Iterate through all on-platform identities, call ``getname()`` on all of it.

            - If there's a name found, return it as the ``user_name`` of :class:`UserNameEntryType`

            - If no name was found, go to the next step

        5. Return the default name of the last iterated on-platform data.

            - ``None`` instead if no on-platform data iterated or there's only one on-platform ID but it's hanging.

        .. note::

            It is better to specify ``channel_data`` whenever it is possible
            because it enables LINE to get the user name in a channel without them adding the bot as friend.

            This methods sends an email report if there is any on-platform OID linked to the root user data found
            but the actual data was not found.

        :param root_oid: oid of the user
        :param channel_data: channel to get the user name
        :param on_not_found: user name to be used if not found
        :return: a `namedtuple` containing the user oid and the user name
        """
        udata = self.find_one_casted({RootUserModel.Id.key: root_oid})

        # Define a `namedtuple` as return type
        UserNameEntry = namedtuple("UserNameEntry", ["user_id", "user_name"])

        # Step 1 - Return `None` if no user data found
        if not udata:
            return None

        # Step 2 - Check if the user name has been set
        if udata.config.name:
            return UserNameEntry(user_id=root_oid, user_name=udata.config.name)

        # Step 3 - Check if there's connected on platform identity
        if not udata.has_onplat_data:
            return UserNameEntry(user_id=root_oid, user_name=on_not_found if on_not_found else f"UID - {root_oid}")

        # Step 4 - Iterate through all on-platform IDs and call `get_name()`
        onplat_data: Optional[OnPlatformUserModel] = None
        for onplatoid in udata.on_plat_oids:
            onplat_data = OnPlatformIdentityManager.get_onplat_by_oid(onplatoid)

            if not onplat_data:
                MailSender.send_email_async(
                    f"On-platform data ID {onplatoid} bound to the root data of ID {root_oid}, but no "
                    f"corresponding on-platform data found.",
                    subject="Data corruption on the link from root user data to onplat"
                )
                continue

            uname = onplat_data.get_name(channel_data)
            if uname:
                return UserNameEntry(user_id=root_oid, user_name=uname)

        # Step 5 - Return the name for last iterated data
        name_str = onplat_data.get_name_str(channel_data) if onplat_data else None
        return UserNameEntry(user_id=root_oid, user_name=on_not_found or name_str)

    def get_root_data_api_token(self, token: str, *, skip_on_plat=True) -> GetRootUserDataResult:
        """
        Get the via API token.

        If ``skip_on_plat`` is ``True``, the returned :class:`GetRootUserDataResult` will contain the on-platform
        identity model if found (cost some performance). Otherwise, the on-platform identity will not be included.

        Sends an email report if on-platform ID was found but the actual data is not found.

        :param token: API token to get the root user data
        :param skip_on_plat: if to skip the process to get the on-platform identity acquiring process
        :return: result of getting the root user data
        """
        api_u_data = APIUserManager.get_user_data_token(token)
        entry = None
        onplat_list = []

        if api_u_data is None:
            outcome = GetOutcome.X_NOT_FOUND_FIRST_QUERY
        else:
            root_u_data = self.get_root_data_api_oid(api_u_data.id)
            if root_u_data is None:
                outcome = GetOutcome.X_NOT_FOUND_SECOND_QUERY
            else:
                entry = root_u_data
                outcome = GetOutcome.O_CACHE_DB

        if not skip_on_plat and outcome.is_success and entry.has_onplat_data:
            missing = []

            for oid in entry.on_plat_oids:
                onplat_data = OnPlatformIdentityManager.get_onplat_by_oid(oid)

                if onplat_data:
                    onplat_list.append(onplat_data)
                else:
                    missing.append(oid)

            if missing:
                MailSender.send_email_async(
                    f"On Platform Data not found while getting the root user data by providing api token.\n"
                    f"API Token: {token} / OID of Missing On Platform Data: {' | '.join([str(i) for i in missing])}",
                    subject="On Platform Data not found")

        return GetRootUserDataResult(outcome, None, entry, api_u_data, onplat_list)

    def get_root_data_onplat(self, platform: Platform, user_token: str, auto_register=True) -> GetRootUserDataResult:
        """
        Get the root user data by providing the credentials of on-platform identity.

        If ``auto_register`` is set to ``True``, the user will be registered when they either missed the data
        for root or on-platform identity.

        ``model_api`` and ``model_onplat_list`` of the returned :class:`GetRootUserDataResult` will be ``None``
        regardless if the result is succeed.

        :param platform: platform of the on-platform identity
        :param user_token: token of the on-platform identity
        :param auto_register: if to register the user automatically
        :return: result of getting theroot user data
        """
        on_plat_data = self.get_onplat_data(platform, user_token)
        rt_user_data = None

        # Check if the on-platform identity exists
        # If not exists and `auto_register`, attempt to register it
        if not on_plat_data and auto_register:
            reg_result = OnPlatformIdentityManager.ensure_register(platform, user_token)

            if not reg_result.success:
                return GetRootUserDataResult(GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT, None, rt_user_data)

            on_plat_data = reg_result.model

        if on_plat_data:
            rt_user_data = self.get_root_data_onplat_oid(on_plat_data.id)

        # Early terminate if the root user data was found
        if rt_user_data:
            return GetRootUserDataResult(GetOutcome.O_CACHE_DB, None, rt_user_data)

        # Early terminate if the root user data was not found but not to auto-register
        if not auto_register:
            return GetRootUserDataResult(GetOutcome.X_NOT_FOUND_ABORTED_INSERT, None, rt_user_data)

        reg_result = self.register_onplat(platform, user_token)

        # Early terminate if failed to register on-platform identity
        if not reg_result.success:
            return GetRootUserDataResult(GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT, None, None)

        return GetRootUserDataResult(GetOutcome.O_ADDED, None, reg_result.model)

    @staticmethod
    @arg_type_ensure
    def get_onplat_data(platform: Platform, user_token: str) -> Optional[OnPlatformUserModel]:
        """
        Get the on-platform user identity by its ``platform`` and ``user_token``.

        :param platform: platform of the user
        :param user_token: token of the user
        :return: `OnPlatformUserModel` if found, `None` otherwise
        """
        return OnPlatformIdentityManager.get_onplat(platform, user_token)

    @staticmethod
    def get_onplat_data_dict() -> Dict[ObjectId, OnPlatformUserModel]:
        """
        Get a :class:`dict` which key is the on-platform identity OID and value is its corresponding user data.

        This :class:`dict` includes all on-platform identity data,
        hence the use of this function should be carefully considered as it's expensive.

        :return: a `dict` containing all on-platform identity data
        """
        ret = {}
        for onplat_data in OnPlatformIdentityManager.find_cursor_with_count():
            ret[onplat_data.id] = onplat_data

        return ret

    def get_root_to_onplat_dict(self, root_oids: Optional[List[ObjectId]] = None) -> Dict[ObjectId, List[ObjectId]]:
        """
        Get a :class:`dict` which key is the root OID and value is the on-plat identity OIDs it has.

        If ``root_oids`` is ``None``, returns all correspondance.

        :param root_oids: root OIDs to get the corresponding on-plat OIDs
        :return: a `dict` of the root OID to on-plat OID correspondance
        """
        ret = {}
        filter_ = {RootUserModel.OnPlatOids.key: {"$exists": True}}

        if root_oids:
            filter_[OID_KEY] = {"$in": root_oids}

        for root_data in self.find_cursor_with_count(filter_):
            ret[root_data.id] = root_data.on_plat_oids

        return ret

    @arg_type_ensure
    def get_root_data_api_oid(self, api_oid: ObjectId) -> Optional[RootUserModel]:
        """
        Get the root user data via its ``api_oid``.

        :param api_oid: API OID of the root user data to get
        :return: `RootUserModel` if found, `None` otherwise
        """
        return self.find_one_casted({RootUserModel.ApiOid.key: api_oid})

    @arg_type_ensure
    def get_root_data_onplat_oid(self, onplat_oid: ObjectId) -> Optional[RootUserModel]:
        """
        Get the root user data via one of its ``onplat_oid``.

        :param onplat_oid: on-platform identity OID of the root user data to get
        :return: `RootUserModel` if found, `None` otherwise
        """
        return self.find_one_casted({RootUserModel.OnPlatOids.key: onplat_oid})

    @arg_type_ensure
    def get_tzinfo_root_oid(self, root_oid: ObjectId) -> tzinfo:
        """
        Get the :class:`tzinfo` configured for ``root_oid``.

        If the user data is not found, return the default :class:`tzinfo`.

        :param root_oid: OID of the user
        :return: tzinfo of the user
        """
        u_data = self.get_root_data_oid(root_oid)
        if not u_data:
            return DEFAULT_LOCALE.to_tzinfo()

        return u_data.config.tzinfo

    @arg_type_ensure
    def get_lang_code_root_oid(self, root_oid: ObjectId) -> Optional[str]:
        """
        Get the language code configured for ``root_oid``.

        If the user data is not found, return the default language code.

        :param root_oid: OID of the user
        :return: language code of the user
        """
        u_data = self.get_root_data_oid(root_oid)
        if not u_data:
            return None

        return u_data.config.language

    @arg_type_ensure
    def get_config_root_oid(self, root_oid: ObjectId) -> RootUserConfigModel:
        """
        Get the :class:`RootUserConfigModel` of ``root_oid``.

        If the user data is not found, return the default :class:`RootUserConfigModel`

        :param root_oid: OID of the user
        :return: `RootUserConfigModel` of the user
        """
        u_data = self.get_root_data_oid(root_oid)
        if not u_data:
            return RootUserConfigModel.generate_default()

        return u_data.config

    @arg_type_ensure
    def merge_onplat_to_api(self, src_root_oid: ObjectId, dest_root_oid: ObjectId) -> OperationOutcome:
        """
        Merge 2 root user data with its OID being the oldest OID among ``src_root_oid`` and ``dest_root_oid``.

        The configs and API OID of ``dest_root_oid`` will be kept.
        Corresponding data from ``src_root_oid`` will be lost.

        :return: `True` if all actions have been acknowledged and success
        """
        if src_root_oid == dest_root_oid:
            return OperationOutcome.X_SAME_SRC_DEST

        src_data = self.find_one({RootUserModel.Id.key: src_root_oid})
        if not src_data:
            return OperationOutcome.X_SRC_DATA_NOT_FOUND
        dest_data = self.find_one({RootUserModel.Id.key: dest_root_oid})
        if not dest_data:
            return OperationOutcome.X_DEST_DATA_NOT_FOUND

        # The actual implementation is to get the data from both source and destination,
        # then calculate the oldest OID as the actual destination,
        # remove source and destination data,
        # then re-insert the data with the oldest ID and the configs / API OID on the destination data
        actual_dst = min(src_root_oid, dest_root_oid)

        ack_rm = self.delete_many({RootUserModel.Id.key: {"$in": [src_root_oid, dest_root_oid]}}).acknowledged

        if not ack_rm:
            return OperationOutcome.X_NOT_DELETED

        data = dest_data
        data[OID_KEY] = actual_dst

        src_op = src_data.get(RootUserModel.OnPlatOids.key, [])

        if RootUserModel.OnPlatOids.key in data:
            data[RootUserModel.OnPlatOids.key].extend(src_op)
        else:
            data[RootUserModel.OnPlatOids.key] = src_op

        _, outcome, _ = self.insert_one_data(from_db=True, **data)

        if not outcome.is_success:
            return OperationOutcome.X_NOT_UPDATED

        return OperationOutcome.O_COMPLETED

    @arg_type_ensure
    def update_config(self, root_oid: ObjectId, **cfg_vars) -> RootUserUpdateResult:
        """
        Update the config of the user ``root_oid``.

        :param root_oid: OID of the user
        :param cfg_vars: new config of the user
        :return: result of the update
        """
        # Filter keys not belong to `RootUserConfigModel`
        update_vars = {fk: fv for fk, fv in cfg_vars.items() if fk in RootUserConfigModel.model_field_keys()}

        updated = self.find_one_and_update(
            {OID_KEY: root_oid},
            {"$set": {RootUserModel.Config.key: RootUserConfigModel(**update_vars)}},
            return_document=ReturnDocument.AFTER)

        if updated:
            updated = RootUserModel.cast_model(updated)
            outcome = UpdateOutcome.O_UPDATED
        else:
            outcome = UpdateOutcome.X_NOT_FOUND

        return RootUserUpdateResult(outcome, None, updated)


APIUserManager = _APIUserManager()
OnPlatformIdentityManager = _OnPlatformIdentityManager()
RootUserManager = _RootUserManager()
