from typing import Optional

from bson import ObjectId

from extutils.gidentity import GoogleIdentityUserData
from models import APIUserModel, OnPlatformUserModel, MixedUserModel

from ._base import BaseCollection
from ._mixin import GenerateTokenMixin
from .results import (
    InsertOutcome, GetOutcome,
    OnSiteUserRegistrationResult, OnPlatformUserRegistrationResult, MixedUserRegistrationResult,
    GetOnSiteUserDataResult
)

DB_NAME = "user"


class APIUserManager(GenerateTokenMixin, BaseCollection):
    token_length = APIUserModel.API_TOKEN_LENGTH
    token_key = APIUserModel.APIToken

    def __init__(self):
        super().__init__(DB_NAME, "api", [APIUserModel.GoogleUniqueID, APIUserModel.APIToken])
        self.create_index(APIUserModel.GoogleUniqueID, unique=True, name="Google Identity Unique ID")
        self.create_index(APIUserModel.APIToken, unique=True, name="Jelly Bot API Token")

    def get_user_data_id_data(self, id_data) -> Optional[APIUserModel]:
        return self.get_user_data_google_id(id_data.uid)

    def get_user_data_token(self, token) -> Optional[APIUserModel]:
        return self.get_cache(APIUserModel.APIToken, token, parse_cls=APIUserModel)

    def get_user_data_google_id(self, goo_uid) -> Optional[APIUserModel]:
        return self.get_cache(APIUserModel.GoogleUniqueID, goo_uid, parse_cls=APIUserModel)

    def register(self, id_data: GoogleIdentityUserData) -> OnSiteUserRegistrationResult:
        token = None
        entry, outcome, ex, insert_result = \
            self.insert_one_data(APIUserModel, email=id_data.email, gid_id=id_data.uid, token=self.generate_hex_token())

        if InsertOutcome.is_inserted(outcome):
            token = entry.token.value
            self.set_cache(APIUserModel.GoogleUniqueID, id_data.uid, entry)
            self.set_cache(APIUserModel.APIToken, token, entry)
        else:
            entry = self.get_user_data_google_id(id_data.uid)
            if entry is None:
                outcome = InsertOutcome.FAILED_CACHE_MISSING_ABORT_INSERT
            else:
                token = entry.token.value

        return OnSiteUserRegistrationResult(outcome, entry, ex, token)


class OnPlatformIdentityManager(BaseCollection):
    def __init__(self):
        super().__init__(DB_NAME, "onplat", OnPlatformUserModel.UserToken)
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


class MixedUserManager(BaseCollection):
    # TODO: ID_CONN / TOKEN - Connect API User and OnPlatform ID
    # TODO: ID_CONN / TOKEN - Mixed User add user name on it - add user name db

    # Changes:
    #     Old: Insert active(parent) mix _id field
    #     New: Insert inactive(child) mix _id field
    #
    #     Each time getting user data:
    #         Check if active/inactive flag exists:
    #             Parent exists: Get to the highest level _id and return
    #
    # When connecting:
    #     Update all data bound on MixUserModel recursively
    #
    # User name -> Another collection and use oid to connect name in MixedUserModel

    def __init__(self):
        super().__init__(DB_NAME, "mix", [MixedUserModel.APIUserID, MixedUserModel.OnPlatformUserIDs])
        self._mgr_api = APIUserManager()
        self._mgr_onplat = OnPlatformIdentityManager()
        self.create_index(MixedUserModel.APIUserID, unique=True, sparse=True, name="API User OID")
        self.create_index(MixedUserModel.OnPlatformUserIDs, unique=True, sparse=True, name="On Platform Identity OIDs")

    def get_user_data_api_oid(self, api_oid: ObjectId) -> Optional[MixedUserModel]:
        return self.get_cache(MixedUserModel.APIUserID, api_oid, parse_cls=MixedUserModel)

    def get_user_data_api_token(self, token: str) -> GetOnSiteUserDataResult:
        entry = self._mgr_api.get_user_data_token(token)

        if entry is None:
            outcome = GetOutcome.FAILED_NOT_FOUND_ABORTED_INSERT
        else:
            outcome = GetOutcome.SUCCESS_CACHE_DB

        return GetOnSiteUserDataResult(outcome, entry)

    def is_api_user_exists(self, token: str) -> bool:
        return GetOutcome.is_success(self.get_user_data_api_token(token).outcome)

    def get_user_data_on_plat_oid(self, onplat_oid: ObjectId) -> Optional[MixedUserModel]:
        return self.get_cache(MixedUserModel.OnPlatformUserIDs, onplat_oid, parse_cls=MixedUserModel)

    def get_user_data_on_plat(self, platform, user_token) -> Optional[OnPlatformUserModel]:
        return self._mgr_onplat.get_onplat(platform, user_token)

    def _register_(self, u_reg_func, get_oid_func, mix_from_oid_func, cache_key, conn_arg_name,
                   oc_onconn_failed, oc_onreg_failed, args, hint="(Unknown)", conn_arg_list=False) \
            -> MixedUserRegistrationResult:
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
                self.insert_one_data(MixedUserModel,
                                     **{conn_arg_name: [user_reg_oid] if conn_arg_list else user_reg_oid})

            if InsertOutcome.is_inserted(build_conn_outcome):
                self.set_cache(cache_key, user_reg_oid, build_conn_entry)
                overall_outcome = InsertOutcome.SUCCESS_INSERTED
            else:
                build_conn_entry = mix_from_oid_func(user_reg_oid)
                if build_conn_entry is None:
                    overall_outcome = oc_onconn_failed
                    build_conn_outcome = InsertOutcome.FAILED_CACHE_MISSING_ATTEMPTED_INSERT
                else:
                    overall_outcome = InsertOutcome.SUCCESS_DATA_EXISTS
        else:
            overall_outcome = oc_onreg_failed

        return MixedUserRegistrationResult(overall_outcome,
                                           build_conn_entry, build_conn_outcome, build_conn_ex, user_reg_result, hint)

    def register_onplat(self, platform, user_token) -> MixedUserRegistrationResult:
        return self._register_(self._mgr_onplat.register, self._mgr_onplat.get_onplat, self.get_user_data_on_plat_oid,
                               MixedUserModel.OnPlatformUserIDs, "onplat_oids",
                               InsertOutcome.FAILED_ON_CONN_ONPLAT, InsertOutcome.FAILED_ON_REG_ONPLAT,
                               (platform, user_token), hint="OnPlatform", conn_arg_list=True)

    def register_google(self, id_data: GoogleIdentityUserData) -> MixedUserRegistrationResult:
        return self._register_(self._mgr_api.register, self._mgr_api.get_user_data_id_data, self.get_user_data_api_oid,
                               MixedUserModel.APIUserID, "api_oid",
                               InsertOutcome.FAILED_ON_CONN_API, InsertOutcome.FAILED_ON_REG_API,
                               (id_data,), hint="APIUser", conn_arg_list=False)


_inst = MixedUserManager()
