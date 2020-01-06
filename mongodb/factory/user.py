from collections import namedtuple
from typing import Optional, Dict, List, Union

from bson import ObjectId
from datetime import tzinfo

from pymongo import ReturnDocument

from extutils.gidentity import GoogleIdentityUserData
from extutils.emailutils import MailSender
from extutils.locales import default_locale
from extutils.checker import param_type_ensure
from flags import Platform
from models import APIUserModel, OnPlatformUserModel, RootUserModel, RootUserConfigModel, OID_KEY, ChannelModel, \
    ChannelCollectionModel
from mongodb.factory.results import OperationOutcome

from ._base import BaseCollection
from ._mixin import GenerateTokenMixin
from .results import (
    WriteOutcome, GetOutcome, UpdateOutcome,
    OnSiteUserRegistrationResult, OnPlatformUserRegistrationResult, RootUserRegistrationResult,
    GetRootUserDataApiResult, RootUserUpdateResult, GetRootUserDataResult
)

DB_NAME = "user"


class APIUserManager(GenerateTokenMixin, BaseCollection):
    token_length = APIUserModel.API_TOKEN_LENGTH
    token_key = APIUserModel.Token.key

    database_name = DB_NAME
    collection_name = "api"
    model_class = APIUserModel

    def __init__(self):
        super().__init__()
        self.create_index(APIUserModel.GoogleUid.key, unique=True, name="Google Identity Unique ID")
        self.create_index(APIUserModel.Token.key, unique=True, name="Jelly Bot API Token")

    def get_user_data_id_data(self, id_data: GoogleIdentityUserData) -> Optional[APIUserModel]:
        return self.get_user_data_google_id(id_data.uid)

    def get_user_data_token(self, token: str) -> Optional[APIUserModel]:
        return self.find_one_casted({APIUserModel.Token.key: token}, parse_cls=APIUserModel)

    def get_user_data_google_id(self, goo_uid: str) -> Optional[APIUserModel]:
        return self.find_one_casted({APIUserModel.GoogleUid.key: goo_uid}, parse_cls=APIUserModel)

    def register(self, id_data: GoogleIdentityUserData) -> OnSiteUserRegistrationResult:
        token = None
        entry, outcome, ex = \
            self.insert_one_data(Email=id_data.email, GoogleUid=id_data.uid, Token=self.generate_hex_token())

        if outcome.is_inserted:
            token = entry.token
        else:
            entry = self.get_user_data_google_id(id_data.uid)
            if entry is None:
                if ex is not None:
                    outcome = WriteOutcome.X_EXCEPTION_OCCURRED
                else:
                    outcome = WriteOutcome.X_CACHE_MISSING_ABORT_INSERT
            else:
                token = entry.token

        return OnSiteUserRegistrationResult(outcome, entry, ex, token)


class OnPlatformIdentityManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "onplat"
    model_class = OnPlatformUserModel

    def __init__(self):
        super().__init__()
        self.create_index([(OnPlatformUserModel.Platform.key, 1), (OnPlatformUserModel.Token.key, 1)],
                          unique=True, name="Compound - Identity")

    @param_type_ensure
    def get_onplat_by_oid(self, oid: ObjectId) -> Optional[OnPlatformUserModel]:
        return self.find_one_casted({OnPlatformUserModel.Id.key: oid}, parse_cls=OnPlatformUserModel)

    @param_type_ensure
    def get_onplat(self, platform: Platform, user_token: str) -> Optional[OnPlatformUserModel]:
        return self.find_one_casted(
            {OnPlatformUserModel.Platform.key: platform, OnPlatformUserModel.Token.key: user_token},
            parse_cls=OnPlatformUserModel)

    @param_type_ensure
    def register(self, platform: Platform, user_token) -> OnPlatformUserRegistrationResult:
        entry, outcome, ex = \
            self.insert_one_data(Token=user_token, Platform=platform)

        if not outcome.is_inserted:
            entry = self.get_onplat(platform, user_token)
            if entry is None:
                outcome = WriteOutcome.X_CACHE_MISSING_ABORT_INSERT

        return OnPlatformUserRegistrationResult(outcome, entry, ex)


class RootUserManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "root"
    model_class = RootUserModel

    def __init__(self):
        super().__init__()
        self._mgr_api = APIUserManager()
        self._mgr_onplat = OnPlatformIdentityManager()
        self.create_index(
            RootUserModel.ApiOid.key, unique=True, name="API User OID",
            partialFilterExpression={RootUserModel.ApiOid.key: {"$exists": True}})
        self.create_index(
            RootUserModel.OnPlatOids.key, unique=True, name="On Platform Identity OIDs",
            partialFilterExpression={RootUserModel.OnPlatOids.key: {"$exists": True}})

    def _register_(self, u_reg_func, get_oid_func, root_from_oid_func, conn_arg_name,
                   oc_onconn_failed, oc_onreg_failed, args, hint="(Unknown)", conn_arg_list=False,
                   on_exist=None) \
            -> RootUserRegistrationResult:
        user_reg_result = u_reg_func(*args)
        user_reg_oid = None
        build_conn_entry = None
        build_conn_outcome = WriteOutcome.X_NOT_EXECUTED
        build_conn_ex = None

        if user_reg_result.outcome.is_inserted:
            user_reg_oid = user_reg_result.model.id
        elif user_reg_result.outcome.data_found:
            get_data = get_oid_func(*args)
            if get_data is not None:
                user_reg_oid = get_data.id

        if user_reg_oid is not None:
            build_conn_entry, build_conn_outcome, build_conn_ex = \
                self.insert_one_data(**{conn_arg_name: [user_reg_oid] if conn_arg_list else user_reg_oid})

            if build_conn_outcome.is_inserted:
                overall_outcome = WriteOutcome.O_INSERTED
            else:
                build_conn_entry = root_from_oid_func(user_reg_oid)
                if build_conn_entry is None:
                    overall_outcome = oc_onconn_failed
                    build_conn_outcome = WriteOutcome.X_CACHE_MISSING_ATTEMPTED_INSERT
                else:
                    overall_outcome = WriteOutcome.O_DATA_EXISTS
                    if on_exist:
                        on_exist()
        else:
            overall_outcome = oc_onreg_failed

        return RootUserRegistrationResult(overall_outcome,
                                          build_conn_entry, build_conn_outcome, build_conn_ex, user_reg_result, hint)

    def is_user_exists(self, api_token: str) -> bool:
        return self.get_root_data_api_token(api_token).success

    def register_onplat(self, platform, user_token) -> RootUserRegistrationResult:
        return self._register_(self._mgr_onplat.register, self._mgr_onplat.get_onplat, self.get_root_data_onplat_oid,
                               "OnPlatOids", WriteOutcome.X_ON_CONN_ONPLAT, WriteOutcome.X_ON_REG_ONPLAT,
                               (platform, user_token), hint="OnPlatform", conn_arg_list=True)

    def register_google(self, id_data: GoogleIdentityUserData) -> RootUserRegistrationResult:
        def on_exist():
            self._mgr_api.update_many_async({APIUserModel.GoogleUid.key: id_data.uid,
                                             APIUserModel.Email.key: {"$ne": id_data.email}},
                                            {"$set": {APIUserModel.Email.key: id_data.email}})

        return self._register_(self._mgr_api.register, self._mgr_api.get_user_data_id_data, self.get_root_data_api_oid,
                               "ApiOid", WriteOutcome.X_ON_CONN_API, WriteOutcome.X_ON_REG_API,
                               (id_data,), hint="APIUser", conn_arg_list=False, on_exist=on_exist)

    @param_type_ensure
    def get_root_data_oid(self, root_oid: ObjectId) -> Optional[RootUserModel]:
        return self.find_one_casted({OID_KEY: root_oid}, parse_cls=RootUserModel)

    @param_type_ensure
    def get_root_data_uname(
            self, root_oid: ObjectId, channel_data: Union[ChannelModel, ChannelCollectionModel, None] = None,
            str_not_found: Optional[str] = None) -> Optional[namedtuple]:
        """
        Get the name of the user with UID = `root_oid`.

        Returns `None` if no corresponding user data found.
        Returns the root oid if no On Platform Identity found.

        :return: namedtuple(user_oid, user_name)
        """
        udata = self.find_one_casted({RootUserModel.Id.key: root_oid}, parse_cls=RootUserModel)

        # No user data found? Return None
        if not udata:
            return None

        UserNameQuery = namedtuple("UserNameQuery", ["user_id", "user_name"])

        # Name has been set?
        if udata.config.name:
            return UserNameQuery(user_id=root_oid, user_name=udata.config.name)

        # On Platform Identity found?
        if udata.has_onplat_data:
            for onplatoid in udata.on_plat_oids:
                onplat_data: Optional[OnPlatformUserModel] = self._mgr_onplat.get_onplat_by_oid(onplatoid)

                if onplat_data:
                    uname = onplat_data.get_name(channel_data)
                    if not uname:
                        if str_not_found:
                            uname = str_not_found
                        else:
                            uname = onplat_data.get_name_str(channel_data)

                    return UserNameQuery(
                        user_id=root_oid, user_name=uname)
                else:
                    MailSender.send_email(
                        f"OnPlatOid {onplatoid} was found to bind with the root data of {root_oid}, but no "
                        f"corresponding On-Platform data found.")

        return None

    def get_root_data_api_token(self, token: str) -> GetRootUserDataApiResult:
        api_u_data = self._mgr_api.get_user_data_token(token)
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

        if outcome.is_success and entry.has_onplat_data:
            missing = []

            for oid in entry.on_plat_oids:
                onplat_data = self._mgr_onplat.get_onplat_by_oid(oid)

                if onplat_data:
                    onplat_list.append(onplat_data)
                else:
                    missing.append(oid)

            if missing:
                MailSender.send_email_async(
                    f"On Platform Data not found while getting the root user data by providing api token.\n"
                    f"API Token: {token} / OID of Missing On Platform Data: {' | '.join([str(i) for i in missing])}",
                    subject="On Platform Data not found")

        return GetRootUserDataApiResult(outcome, entry, api_u_data, onplat_list)

    @param_type_ensure
    def get_onplat_data(self, platform: Platform, user_token: str) -> Optional[OnPlatformUserModel]:
        return self._mgr_onplat.get_onplat(platform, user_token)

    def get_onplat_data_dict(self) -> Dict[ObjectId, OnPlatformUserModel]:
        ret = {}
        for d in self._mgr_onplat.find_cursor_with_count({}, parse_cls=OnPlatformUserModel):
            ret[d.id] = d

        return ret

    def get_onplat_to_root_dict(self) -> Dict[ObjectId, ObjectId]:
        ret = {}
        for d in self.find_cursor_with_count({}, parse_cls=RootUserModel):
            if d.has_onplat_data:
                for onplat_oid in d.on_plat_oids:
                    ret[onplat_oid] = d.id

        return ret

    def get_root_to_onplat_dict(self) -> Dict[ObjectId, List[ObjectId]]:
        ret = {}
        for d in self.find_cursor_with_count(
                {RootUserModel.OnPlatOids.key: {"$exists": True}}, parse_cls=RootUserModel):
            ret[d.id] = d.on_plat_oids

        return ret

    @param_type_ensure
    def get_root_data_api_oid(self, api_oid: ObjectId) -> Optional[RootUserModel]:
        return self.find_one_casted({RootUserModel.ApiOid.key: api_oid}, parse_cls=RootUserModel)

    def get_root_data_onplat(self, platform: Platform, user_token: str, auto_register=True) -> GetRootUserDataResult:
        on_plat_data = self.get_onplat_data(platform, user_token)
        rt_user_data = None

        if on_plat_data is None and auto_register:
            on_plat_reg_result = self._mgr_onplat.register(platform, user_token)

            if on_plat_reg_result.success:
                on_plat_data = self.get_onplat_data(platform, user_token)

        if on_plat_data is None:
            outcome = GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT
        else:
            rt_user_data = self.get_root_data_onplat_oid(on_plat_data.id)

            if rt_user_data is None:
                if auto_register:
                    reg_result = self.register_onplat(platform, user_token)

                    if reg_result.success:
                        rt_user_data = reg_result.model
                        outcome = GetOutcome.O_ADDED
                    else:
                        outcome = GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT
                else:
                    outcome = GetOutcome.X_NOT_FOUND_ABORTED_INSERT
            else:
                outcome = GetOutcome.O_CACHE_DB

        return GetRootUserDataResult(outcome, rt_user_data)

    @param_type_ensure
    def get_root_data_onplat_oid(self, onplat_oid: ObjectId) -> Optional[RootUserModel]:
        return self.find_one_casted({RootUserModel.OnPlatOids.key: onplat_oid}, parse_cls=RootUserModel)

    @param_type_ensure
    def get_tzinfo_root_oid(self, root_oid: ObjectId) -> tzinfo:
        u_data = self.get_root_data_oid(root_oid)
        if u_data is None:
            return default_locale.to_tzinfo()
        else:
            return u_data.config.tzinfo

    @param_type_ensure
    def get_lang_code_root_oid(self, root_oid: ObjectId) -> Optional[str]:
        u_data = self.get_root_data_oid(root_oid)
        if u_data is None:
            return None
        else:
            return u_data.config.language

    @param_type_ensure
    def get_config_root_oid(self, root_oid: ObjectId) -> RootUserConfigModel:
        u_data = self.get_root_data_oid(root_oid)
        if u_data is None:
            return RootUserConfigModel.generate_default()
        else:
            return u_data.config

    @param_type_ensure
    def merge_onplat_to_api(self, src_root_oid: ObjectId, dest_root_oid: ObjectId) -> OperationOutcome:
        """
        Merge 2 root user data to be the same. Only the data of `dest_root_oid` will be kept.

        :return: True if all actions have been acknowledged and success.
        """
        if src_root_oid == dest_root_oid:
            return OperationOutcome.X_SAME_SRC_DEST

        src_data = self.find_one({RootUserModel.Id.key: src_root_oid})
        if not src_data:
            return OperationOutcome.X_SRC_DATA_NOT_FOUND
        dest_data = self.find_one({RootUserModel.Id.key: dest_root_oid})
        if not dest_data:
            return OperationOutcome.X_DEST_DATA_NOT_FOUND

        ack_rm = self.delete_one({RootUserModel.Id.key: src_root_oid}).acknowledged
        if ack_rm:
            outcome = self.update_many_outcome(
                {RootUserModel.Id.key: dest_data[RootUserModel.Id.key]},
                {"$push": {RootUserModel.OnPlatOids.key: {"$each": src_data[RootUserModel.OnPlatOids.key]}}})

            if outcome.is_success:
                return OperationOutcome.O_COMPLETED
            else:
                return OperationOutcome.X_NOT_UPDATED
        else:
            return OperationOutcome.X_NOT_DELETED

    @param_type_ensure
    def update_config(self, root_oid: ObjectId, **cfg_vars) -> RootUserUpdateResult:
        updated = self.find_one_and_update(
            {OID_KEY: root_oid},
            {"$set": {RootUserModel.Config.key: RootUserConfigModel(**cfg_vars)}},
            return_document=ReturnDocument.AFTER)

        if updated:
            updated = RootUserConfigModel.cast_model(updated)
            outcome = UpdateOutcome.O_UPDATED
        else:
            outcome = UpdateOutcome.X_NOT_FOUND

        return RootUserUpdateResult(outcome, updated)


_inst = RootUserManager()
