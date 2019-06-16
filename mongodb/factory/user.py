from typing import Optional

from bson import ObjectId
from datetime import tzinfo

from pymongo import ReturnDocument

from extutils.gidentity import GoogleIdentityUserData
from extutils.locales import default_locale, LocaleInfo
from models import APIUserModel, OnPlatformUserModel, RootUserModel, RootUserConfigModel, OID_KEY

from ._base import BaseCollection
from ._mixin import GenerateTokenMixin
from .results import (
    InsertOutcome, GetOutcome, UpdateOutcome,
    OnSiteUserRegistrationResult, OnPlatformUserRegistrationResult, RootUserRegistrationResult,
    GetRootUserDataResult, RootUserUpdateResult
)

DB_NAME = "user"


class APIUserManager(GenerateTokenMixin, BaseCollection):
    token_length = APIUserModel.API_TOKEN_LENGTH
    token_key = APIUserModel.APIToken

    database_name = DB_NAME
    collection_name = "api"
    model_class = APIUserModel

    def __init__(self):
        super().__init__(OID_KEY)
        self.create_index(APIUserModel.GoogleUniqueID, unique=True, name="Google Identity Unique ID")
        self.create_index(APIUserModel.APIToken, unique=True, name="Jelly Bot API Token")

    def get_user_data_id_data(self, id_data: GoogleIdentityUserData) -> Optional[APIUserModel]:
        return self.get_user_data_google_id(id_data.uid)

    def get_user_data_token(self, token: str) -> Optional[APIUserModel]:
        return self.get_cache_condition(
            OID_KEY, lambda x: x.token.value == token, ({APIUserModel.APIToken: token},),
            parse_cls=APIUserModel)

    def get_user_data_google_id(self, goo_uid: str) -> Optional[APIUserModel]:
        return self.get_cache_condition(
            OID_KEY, lambda x: x.gid_id.value == goo_uid, ({APIUserModel.GoogleUniqueID: goo_uid},),
            parse_cls=APIUserModel)

    def register(self, id_data: GoogleIdentityUserData) -> OnSiteUserRegistrationResult:
        token = None
        entry, outcome, ex, insert_result = \
            self.insert_one_data(APIUserModel, email=id_data.email, gid_id=id_data.uid, token=self.generate_hex_token())

        if InsertOutcome.is_inserted(outcome):
            token = entry.token.value
            self.set_cache(OID_KEY, entry.id.value, entry, parse_cls=APIUserModel)
        else:
            entry = self.get_user_data_google_id(id_data.uid)
            if entry is None:
                outcome = InsertOutcome.FAILED_CACHE_MISSING_ABORT_INSERT
            else:
                token = entry.token.value

        return OnSiteUserRegistrationResult(outcome, entry, ex, token)


class OnPlatformIdentityManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "onplat"
    model_class = OnPlatformUserModel

    def __init__(self):
        super().__init__(OnPlatformUserModel.UserToken)
        self.create_index([(OnPlatformUserModel.Platform, 1), (OnPlatformUserModel.UserToken, 1)],
                          unique=True, name="Compound - Identity")

    def get_onplat(self, platform, user_token) -> Optional[OnPlatformUserModel]:
        return self.get_cache(OnPlatformUserModel.UserToken, (platform, user_token),
                              parse_cls=OnPlatformUserModel,
                              acquire_args=({OnPlatformUserModel.Platform: platform,
                                             OnPlatformUserModel.UserToken: user_token},))

    def register(self, platform, user_token) -> OnPlatformUserRegistrationResult:
        entry, outcome, ex, insert_result = \
            self.insert_one_data(OnPlatformUserModel, token=user_token, platform=platform)

        if InsertOutcome.is_inserted(outcome):
            self.set_cache(OnPlatformUserModel.UserToken, (platform, user_token), entry)
        else:
            entry = self.get_onplat(platform, user_token)
            if entry is None:
                outcome = InsertOutcome.FAILED_CACHE_MISSING_ABORT_INSERT

        return OnPlatformUserRegistrationResult(outcome, entry, ex)


class RootUserManager(BaseCollection):
    # TODO: ID_CONN / TOKEN - Connect API User and OnPlatform ID - migrate() check:
    #   - AutoReplyConnection.CreatorOID (ar.conn.cr)
    #   - AutoReplyConnection.ExcludedOIDs (ar.conn.e[])
    #   - ChannelPermissionProfile.UserID (channel.perm.u)
    #   - Channel.ManagerOIDs (channel.dict.mgr[])
    #   - TokenAction.CreatorOID (tk_act.main.cr)
    #   Then check if the old user.mix identity is removed or not
    database_name = DB_NAME
    collection_name = "root"
    model_class = RootUserModel

    def __init__(self):
        super().__init__(OID_KEY)
        self._mgr_api = APIUserManager()
        self._mgr_onplat = OnPlatformIdentityManager()
        self.create_index(RootUserModel.APIUserID, unique=True, sparse=True, name="API User OID")
        self.create_index(RootUserModel.OnPlatformUserIDs, unique=True, sparse=True, name="On Platform Identity OIDs")

    def _register_(self, u_reg_func, get_oid_func, root_from_oid_func, cache_key, conn_arg_name,
                   oc_onconn_failed, oc_onreg_failed, args, hint="(Unknown)", conn_arg_list=False) \
            -> RootUserRegistrationResult:
        user_reg_result = u_reg_func(*args)
        user_reg_oid = None
        build_conn_entry = None
        build_conn_outcome = InsertOutcome.FAILED_NOT_EXECUTED
        build_conn_ex = None

        if InsertOutcome.is_inserted(user_reg_result.outcome):
            user_reg_oid = user_reg_result.model.id.value
        elif InsertOutcome.data_found(user_reg_result.outcome):
            get_data = get_oid_func(*args)
            if get_data is not None:
                user_reg_oid = get_data.id.value

        if user_reg_oid is not None:
            build_conn_entry, build_conn_outcome, build_conn_ex, insert_result = \
                self.insert_one_data(RootUserModel,
                                     **{conn_arg_name: [user_reg_oid] if conn_arg_list else user_reg_oid})

            if InsertOutcome.is_inserted(build_conn_outcome):
                self.set_cache(cache_key, user_reg_oid, build_conn_entry)
                overall_outcome = InsertOutcome.SUCCESS_INSERTED
            else:
                build_conn_entry = root_from_oid_func(user_reg_oid)
                if build_conn_entry is None:
                    overall_outcome = oc_onconn_failed
                    build_conn_outcome = InsertOutcome.FAILED_CACHE_MISSING_ATTEMPTED_INSERT
                else:
                    overall_outcome = InsertOutcome.SUCCESS_DATA_EXISTS
        else:
            overall_outcome = oc_onreg_failed

        return RootUserRegistrationResult(overall_outcome,
                                          build_conn_entry, build_conn_outcome, build_conn_ex, user_reg_result, hint)

    def is_user_exists(self, api_token: str) -> bool:
        return self.get_root_data_api_token(api_token).success

    def register_onplat(self, platform, user_token) -> RootUserRegistrationResult:
        return self._register_(self._mgr_onplat.register, self._mgr_onplat.get_onplat, self.get_root_data_on_plat_oid,
                               RootUserModel.OnPlatformUserIDs, "onplat_oids",
                               InsertOutcome.FAILED_ON_CONN_ONPLAT, InsertOutcome.FAILED_ON_REG_ONPLAT,
                               (platform, user_token), hint="OnPlatform", conn_arg_list=True)

    def register_google(self, id_data: GoogleIdentityUserData) -> RootUserRegistrationResult:
        return self._register_(self._mgr_api.register, self._mgr_api.get_user_data_id_data, self.get_root_data_api_oid,
                               RootUserModel.APIUserID, "api_oid",
                               InsertOutcome.FAILED_ON_CONN_API, InsertOutcome.FAILED_ON_REG_API,
                               (id_data,), hint="APIUser", conn_arg_list=False)

    def get_root_data_api_oid(self, api_oid: [ObjectId, str]) -> Optional[RootUserModel]:
        if isinstance(api_oid, str):
            api_oid = ObjectId(api_oid)

        return self.get_cache_condition(
            OID_KEY, lambda item: item.api_oid.value == api_oid, ({RootUserModel.APIUserID: api_oid},),
            parse_cls=RootUserModel)

    def get_root_data_api_token(self, token: str) -> GetRootUserDataResult:
        api_u_data = self._mgr_api.get_user_data_token(token)
        entry = None

        if api_u_data is None:
            outcome = GetOutcome.FAILED_NOT_FOUND_FIRST_QUERY
        else:
            root_u_data = self.get_root_data_api_oid(api_u_data.id.value)
            if root_u_data is None:
                outcome = GetOutcome.FAILED_NOT_FOUND_SECOND_QUERY
            else:
                entry = root_u_data
                outcome = GetOutcome.SUCCESS_CACHE_DB

        return GetRootUserDataResult(outcome, entry, api_u_data)

    def get_root_data_on_plat_oid(self, onplat_oid: [ObjectId, str]) -> Optional[RootUserModel]:
        if isinstance(onplat_oid, str):
            onplat_oid = ObjectId(onplat_oid)

        return self.get_cache_condition(
            OID_KEY, lambda item: onplat_oid in item.api_oids.value, ({RootUserModel.OnPlatformUserIDs: onplat_oid},),
            parse_cls=RootUserModel)

    def get_onplat_data(self, platform, user_token) -> Optional[OnPlatformUserModel]:
        return self._mgr_onplat.get_onplat(platform, user_token)

    def get_tzinfo_root_oid(self, root_oid: ObjectId) -> tzinfo:
        u_data = self.get_root_data_api_oid(root_oid)
        if u_data is None:
            return default_locale.to_tzinfo()
        else:
            return LocaleInfo.get_tzinfo(u_data.config.value.locale.value)

    def get_config_root_oid(self, root_oid: ObjectId) -> RootUserConfigModel:
        u_data = self.get_cache(OID_KEY, root_oid, parse_cls=RootUserModel)
        if u_data is None:
            return RootUserConfigModel.create_default()
        else:
            return u_data.config.value

    def update_config(self, root_oid: ObjectId, **cfg_vars) -> RootUserUpdateResult:
        upd_data = self.set_cache(
            OID_KEY,
            str(root_oid),
            self.find_one_and_update(
                {OID_KEY: root_oid},
                {"$set": {
                    RootUserModel.Config: RootUserConfigModel(
                        **cfg_vars, from_db=False, incl_oid=False).serialize(include_oid=False)}},
                return_document=ReturnDocument.AFTER),
            RootUserModel)

        if upd_data is None:
            outcome = UpdateOutcome.FAILED_NOT_FOUND
        else:
            outcome = UpdateOutcome.SUCCESS_UPDATED

        return RootUserUpdateResult(outcome, upd_data)


_inst = RootUserManager()
