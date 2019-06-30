import pymongo
from bson import ObjectId

from django.utils.translation import gettext_lazy as _

from mongodb.factory import ChannelManager
from mongodb.factory.results import InsertOutcome, GetOutcome, GetPermissionProfileResult, CreatePermissionProfileResult
from models import (
    OID_KEY, ChannelConfigModel,
    ChannelPermissionProfileModel, ChannelPermissionConnectionModel, PermissionPromotionRecordModel
)

from ._base import BaseCollection

DB_NAME = "channel"


class PermissionConnectionManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "user"
    model_class = ChannelPermissionConnectionModel

    def __init__(self):
        super().__init__(self.CACHE_KEY_COMB1)
        self.create_index(
            ChannelPermissionConnectionModel.UserOid.key, name="Permission Connection Identity", unique=True)

    def user_attach_profile(self, channel_oid: ObjectId, user_oid: ObjectId, profile_oid: ObjectId) \
            -> ChannelPermissionConnectionModel:
        """
        Attach `ChannelPermissionProfileModel` and return the attached data.
        """
        id_ = self.update_one(
            {ChannelPermissionConnectionModel.ChannelOid.key: channel_oid,
             ChannelPermissionConnectionModel.UserOid.key: user_oid},
            {"$addToSet": {ChannelPermissionConnectionModel.ProfileOids.key: profile_oid}}, upsert=True).upserted_id

        if id_:
            model = self.find_one({OID_KEY: id_})

            if not model:
                raise ValueError("`upserted_id` exists but no corresponding model found.")
        else:
            model = self.find_one({ChannelPermissionConnectionModel.UserOid.key: user_oid})

            if not model:
                raise ValueError("`Model` should exists because `upserted_id` not exists, "
                                 "however no corresponding model found.")

        return self.set_cache(
            self.CACHE_KEY_COMB1, (channel_oid, user_oid), model, parse_cls=ChannelPermissionConnectionModel)


class PermissionProfileManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "perm"
    model_class = ChannelPermissionProfileModel

    def __init__(self):
        super().__init__(OID_KEY)
        self.create_index(
            [(ChannelPermissionProfileModel.ChannelOid.key, pymongo.DESCENDING),
             (ChannelPermissionProfileModel.Name.key, pymongo.ASCENDING)],
            name="Permission Profile Identity", unique=True)

    def get_default_profile(self, channel_oid: ObjectId) -> GetPermissionProfileResult:
        ex = None

        cnl = ChannelManager.get_channel_oid(channel_oid)
        if not cnl:
            return GetPermissionProfileResult(GetOutcome.X_CHANNEL_NOT_FOUND, None, ex)

        try:
            prof_oid = cnl.config.default_profile_oid
        except AttributeError:
            return GetPermissionProfileResult(GetOutcome.X_CHANNEL_CONFIG_ERROR, None, ex)

        if not cnl.config.is_field_none("DefaultProfileOid"):
            perm_prof = self.get_cache(OID_KEY, prof_oid, parse_cls=ChannelPermissionProfileModel)

            if perm_prof:
                return GetPermissionProfileResult(GetOutcome.O_CACHE_DB, perm_prof, ex)

        create_result = self.create_default_profile(channel_oid)

        return GetPermissionProfileResult(
            GetOutcome.O_ADDED if create_result.success else GetOutcome.X_DEFAULT_PROFILE_ERROR,
            create_result.model, ex)

    def create_default_profile(self, channel_oid: ObjectId) -> CreatePermissionProfileResult:
        default_profile, outcome, ex, insert_result = self.create_profile(channel_oid, Name=_("Default User"))

        if outcome.is_success:
            self.set_cache(OID_KEY, default_profile.id, default_profile, parse_cls=ChannelPermissionProfileModel)
            set_success = ChannelManager.set_config(
                channel_oid, ChannelConfigModel.DefaultProfileOid.key, default_profile)

            if not set_success:
                outcome = InsertOutcome.X_ON_SET_CONFIG

        return CreatePermissionProfileResult(outcome, default_profile, ex)

    def create_profile(self, channel_oid: ObjectId, **fk_param):
        return self.insert_one_data(
            ChannelPermissionProfileModel, ChannelOid=channel_oid, **fk_param)

    # INCOMPLETE: Permission - Ensure mod/admin promotable if the mod/admin to be demoted is the last
    # INCOMPLETE: Permission - Custom permission profile creation (name and color changable only) - create then change
    pass


class PermissionPromotionStatusHolder(BaseCollection):
    database_name = DB_NAME
    collection_name = "promo"
    model_class = PermissionPromotionRecordModel

    # INCOMPLETE: Permission/Promotion - Keeps the promo record for a short period
    # INCOMPLETE: Promote for any role who needs promotion or direct assignment
    pass


class PermissionManager:
    def __init__(self):
        self._conn = PermissionConnectionManager()
        self._perm = PermissionProfileManager()
        self._promo = PermissionPromotionStatusHolder()

    def register_new_default(self, channel_oid: ObjectId, user_oid: ObjectId):
        default_prof = self._perm.get_default_profile(channel_oid)
        if default_prof.success:
            self._conn.user_attach_profile(channel_oid, user_oid, default_prof.model.id)


_inst = PermissionManager()
