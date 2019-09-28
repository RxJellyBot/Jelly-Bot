from typing import Optional

from bson import ObjectId
from datetime import tzinfo

from pymongo import ReturnDocument

from extutils.gidentity import GoogleIdentityUserData
from extutils.locales import default_locale, LocaleInfo
from extutils.checker import DecoParamCaster
from flags import Platform
from models import APIUserModel, OnPlatformUserModel, RootUserModel, RootUserConfigModel, OID_KEY

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
        entry, outcome, ex, insert_result = \
            self.insert_one_data(
                APIUserModel, Email=id_data.email, GoogleUid=id_data.uid, Token=self.generate_hex_token())

        if WriteOutcome.is_inserted(outcome):
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

    @DecoParamCaster({1: Platform, 2: str})
    def get_onplat(self, platform: [int, Platform], user_token: str) -> Optional[OnPlatformUserModel]:
        return self.find_one_casted(
            {OnPlatformUserModel.Platform.key: platform, OnPlatformUserModel.Token.key: user_token},
            parse_cls=OnPlatformUserModel)

    @DecoParamCaster({1: Platform})
    def register(self, platform, user_token) -> OnPlatformUserRegistrationResult:
        entry, outcome, ex, insert_result = \
            self.insert_one_data(OnPlatformUserModel, Token=user_token, Platform=platform)

        if not WriteOutcome.is_inserted(outcome):
            entry = self.get_onplat(platform, user_token)
            if entry is None:
                outcome = WriteOutcome.X_CACHE_MISSING_ABORT_INSERT

        return OnPlatformUserRegistrationResult(outcome, entry, ex)


class RootUserManager(BaseCollection):
    # FIXME: ID_CONN / TOKEN - Connect API User and OnPlatform ID - integrate() check:
    #   Check config confliction
    #   Then check if the old user.mix identity is removed or not
    database_name = DB_NAME
    collection_name = "root"
    model_class = RootUserModel

    def __init__(self):
        super().__init__()
        self._mgr_api = APIUserManager()
        self._mgr_onplat = OnPlatformIdentityManager()
        self.create_index(RootUserModel.ApiOid.key, unique=True, sparse=True, name="API User OID")
        self.create_index(RootUserModel.OnPlatOids.key, unique=True, sparse=True, name="On Platform Identity OIDs")

    def _register_(self, u_reg_func, get_oid_func, root_from_oid_func, conn_arg_name,
                   oc_onconn_failed, oc_onreg_failed, args, hint="(Unknown)", conn_arg_list=False) \
            -> RootUserRegistrationResult:
        user_reg_result = u_reg_func(*args)
        user_reg_oid = None
        build_conn_entry = None
        build_conn_outcome = WriteOutcome.X_NOT_EXECUTED
        build_conn_ex = None

        if WriteOutcome.is_inserted(user_reg_result.outcome):
            user_reg_oid = user_reg_result.model.id
        elif WriteOutcome.data_found(user_reg_result.outcome):
            get_data = get_oid_func(*args)
            if get_data is not None:
                user_reg_oid = get_data.id

        if user_reg_oid is not None:
            build_conn_entry, build_conn_outcome, build_conn_ex, insert_result = \
                self.insert_one_data(RootUserModel,
                                     **{conn_arg_name: [user_reg_oid] if conn_arg_list else user_reg_oid})

            if WriteOutcome.is_inserted(build_conn_outcome):
                overall_outcome = WriteOutcome.O_INSERTED
            else:
                build_conn_entry = root_from_oid_func(user_reg_oid)
                if build_conn_entry is None:
                    overall_outcome = oc_onconn_failed
                    build_conn_outcome = WriteOutcome.X_CACHE_MISSING_ATTEMPTED_INSERT
                else:
                    overall_outcome = WriteOutcome.O_DATA_EXISTS
        else:
            overall_outcome = oc_onreg_failed

        return RootUserRegistrationResult(overall_outcome,
                                          build_conn_entry, build_conn_outcome, build_conn_ex, user_reg_result, hint)

    @DecoParamCaster({1: Platform, 2: str})
    def _get_onplat_data_(self, platform: [int, Platform], user_token: str) -> Optional[OnPlatformUserModel]:
        return self._mgr_onplat.get_onplat(platform, user_token)

    def is_user_exists(self, api_token: str) -> bool:
        return self.get_root_data_api_token(api_token).success

    def register_onplat(self, platform, user_token) -> RootUserRegistrationResult:
        return self._register_(self._mgr_onplat.register, self._mgr_onplat.get_onplat, self.get_root_data_onplat_oid,
                               "OnPlatOids", WriteOutcome.X_ON_CONN_ONPLAT, WriteOutcome.X_ON_REG_ONPLAT,
                               (platform, user_token), hint="OnPlatform", conn_arg_list=True)

    def register_google(self, id_data: GoogleIdentityUserData) -> RootUserRegistrationResult:
        return self._register_(self._mgr_api.register, self._mgr_api.get_user_data_id_data, self.get_root_data_api_oid,
                               "ApiOid", WriteOutcome.X_ON_CONN_API, WriteOutcome.X_ON_REG_API,
                               (id_data,), hint="APIUser", conn_arg_list=False)

    @DecoParamCaster({1: ObjectId})
    def get_root_data_oid(self, root_oid: ObjectId) -> Optional[RootUserModel]:
        return self.find_one_casted({OID_KEY: root_oid}, parse_cls=RootUserModel)

    def get_root_data_api_token(self, token: str) -> GetRootUserDataApiResult:
        api_u_data = self._mgr_api.get_user_data_token(token)
        entry = None

        if api_u_data is None:
            outcome = GetOutcome.X_NOT_FOUND_FIRST_QUERY
        else:
            root_u_data = self.get_root_data_api_oid(api_u_data.id)
            if root_u_data is None:
                outcome = GetOutcome.X_NOT_FOUND_SECOND_QUERY
            else:
                entry = root_u_data
                outcome = GetOutcome.O_CACHE_DB

        return GetRootUserDataApiResult(outcome, entry, api_u_data)

    @DecoParamCaster({1: ObjectId})
    def get_root_data_api_oid(self, api_oid: [ObjectId, str]) -> Optional[RootUserModel]:
        return self.find_one_casted({RootUserModel.ApiOid.key: api_oid}, parse_cls=RootUserModel)

    @DecoParamCaster({1: Platform, 2: str})
    def get_root_data_onplat(self, platform, user_token, auto_register=True) -> GetRootUserDataResult:
        on_plat_data = self._get_onplat_data_(platform, user_token)
        rt_user_data = None

        if on_plat_data is None and auto_register:
            on_plat_reg_result = self._mgr_onplat.register(platform, user_token)

            if on_plat_reg_result.success:
                on_plat_data = self._get_onplat_data_(platform, user_token)

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

    @DecoParamCaster({1: ObjectId})
    def get_root_data_onplat_oid(self, onplat_oid: [ObjectId, str]) -> Optional[RootUserModel]:
        return self.find_one_casted({RootUserModel.OnPlatOids.key: onplat_oid}, parse_cls=RootUserModel)

    @DecoParamCaster({1: ObjectId})
    def get_tzinfo_root_oid(self, root_oid: ObjectId) -> tzinfo:
        u_data = self.get_root_data_oid(root_oid)
        if u_data is None:
            return default_locale.to_tzinfo()
        else:
            return LocaleInfo.get_tzinfo(u_data.config.locale)

    @DecoParamCaster({1: ObjectId})
    def get_config_root_oid(self, root_oid: ObjectId) -> RootUserConfigModel:
        u_data = self.get_root_data_oid(root_oid)
        if u_data is None:
            return RootUserConfigModel.generate_default()
        else:
            return u_data.config

    @DecoParamCaster({1: ObjectId})
    def update_config(self, root_oid: ObjectId, **cfg_vars) -> RootUserUpdateResult:
        updated = self.find_one_and_update(
            {OID_KEY: root_oid},
            {"$set": {RootUserModel.Config.key: RootUserConfigModel(**cfg_vars)}},
            return_document=ReturnDocument.AFTER)

        if updated:
            updated = self.cast_model(updated, parse_cls=RootUserConfigModel)
            outcome = UpdateOutcome.O_UPDATED
        else:
            outcome = UpdateOutcome.X_NOT_FOUND

        return RootUserUpdateResult(outcome, updated)


_inst = RootUserManager()
