from typing import Optional, List

import pymongo
from bson import ObjectId

from django.utils.translation import gettext_lazy as _

from extutils.gmail import MailSender
from mongodb.factory import ChannelManager
from mongodb.factory.results import InsertOutcome, GetOutcome, GetPermissionProfileResult, CreatePermissionProfileResult
from mongodb.utils import CheckableCursor
from models import (
    OID_KEY, ChannelConfigModel, ChannelPermConnDisplayModel,
    ChannelPermissionProfileModel, ChannelPermissionConnectionModel, PermissionPromotionRecordModel
)

from ._base import BaseCollection

DB_NAME = "channel"


class PermissionConnectionManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "user"
    model_class = ChannelPermissionConnectionModel

    def __init__(self):
        super().__init__(self.CACHE_KEY_SPEC1)
        self.create_index(
            [(ChannelPermissionConnectionModel.UserOid.key, pymongo.DESCENDING),
             (ChannelPermissionConnectionModel.ChannelOid.key, pymongo.DESCENDING)],
            name="Permission Connection Identity",
            unique=True)

    def user_attach_profile(self, channel_oid: ObjectId, root_uid: ObjectId, profile_oid: ObjectId) \
            -> ChannelPermissionConnectionModel:
        """
        Attach `ChannelPermissionProfileModel` and return the attached data.
        """
        id_ = self.update_one(
            {ChannelPermissionConnectionModel.ChannelOid.key: channel_oid,
             ChannelPermissionConnectionModel.UserOid.key: root_uid},
            {"$addToSet": {ChannelPermissionConnectionModel.ProfileOids.key: profile_oid}}, upsert=True).upserted_id

        if id_:
            model = self.find_one({OID_KEY: id_})

            if not model:
                raise ValueError("`upserted_id` exists but no corresponding model found.")
        else:
            model = self.find_one({ChannelPermissionConnectionModel.UserOid.key: root_uid})

            if not model:
                raise ValueError("`Model` should exists because `upserted_id` not exists, "
                                 "however no corresponding model found.")

        return self.set_cache(
            self.CACHE_KEY_SPEC1, (channel_oid, root_uid), model, parse_cls=ChannelPermissionConnectionModel)

    # INCOMPLETE: user_detach_profile and delete

    def get_user_profile_oid(self, channel_oid: ObjectId, root_uid: ObjectId) -> ObjectId:
        """
        Gets the profile oid of the specified user.

        :return: `None` if not found.
        """
        return self.get_cache(
            self.CACHE_KEY_SPEC1, (channel_oid, root_uid),
            parse_cls=ChannelPermissionConnectionModel,
            item_key_from_data=(ChannelPermissionConnectionModel.ChannelOid.key,
                                ChannelPermissionConnectionModel.UserOid.key))

    def get_user_connection_cursor(self, root_uid: ObjectId) -> CheckableCursor:
        return CheckableCursor(self.find({ChannelPermissionConnectionModel.UserOid.key: root_uid}),
                               parse_cls=ChannelPermissionConnectionModel)



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

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelPermissionProfileModel]:
        return self.get_cache(OID_KEY, profile_oid, parse_cls=ChannelPermissionProfileModel)

    def get_default_profile(self, channel_oid: ObjectId) -> GetPermissionProfileResult:
        """
        Automatically creates a default profile for `channel_oid` if not exists.
        """
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
        default_profile, outcome, ex, insert_result = self._create_profile_(channel_oid, Name=_("Default User"))

        if outcome.is_success:
            self.set_cache(OID_KEY, default_profile.id, default_profile, parse_cls=ChannelPermissionProfileModel)
            set_success = ChannelManager.set_config(
                channel_oid, ChannelConfigModel.DefaultProfileOid.key, default_profile)

            if not set_success:
                outcome = InsertOutcome.X_ON_SET_CONFIG

        return CreatePermissionProfileResult(outcome, default_profile, ex)

    def _create_profile_(self, channel_oid: ObjectId, **fk_param):
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

    def register_new_default(self, channel_oid: ObjectId, root_uid: ObjectId):
        default_prof = self._perm.get_default_profile(channel_oid)
        if default_prof.success:
            self._conn.user_attach_profile(channel_oid, root_uid, default_prof.model.id)

    def get_user_permission_profile(self, channel_oid: ObjectId, root_uid: ObjectId):
        """
        Gets the profile of the specified user.

        :return: `None` if not found.
        """
        # FIXME: Will be used for displaying the user's permission in Channel/Manage/<Channel ID> page
        return self._conn.get_user_profile_oid(channel_oid, root_uid)

    def get_user_channel_profile_list(self, root_uid: Optional[ObjectId]) -> List[ChannelPermConnDisplayModel]:
        if root_uid is None:
            return []

        ret = []

        not_found_channel = []
        not_found_prof_oids_dict = {}

        crs = self._conn.get_user_connection_cursor(root_uid)

        for d in crs:
            not_found_prof_oids = []

            # Get Channel Model
            cnl = ChannelManager.get_channel_oid(d.channel_oid)

            if cnl is None:
                not_found_channel.append(d.channel_oid)
                continue

            # Get Profile Model
            prof = []
            for p in d.profile_oids:
                pm = self._perm.get_profile(p)
                if pm:
                    prof.append(pm)
                else:
                    not_found_prof_oids.append(p)

            if len(prof) == 0:
                not_found_prof_oids_dict[d.channel_oid] = []
            elif len(not_found_prof_oids) > 0:
                not_found_prof_oids_dict[d.channel_oid] = not_found_prof_oids
            else:
                ret.append(ChannelPermConnDisplayModel(channel=cnl, profiles=prof))

        if len(not_found_channel) > 0 or len(not_found_prof_oids_dict) > 0:
            not_found_prof_oids_txt = "\n".join(
                [f'{cnl_id}: {" / ".join(prof_ids)}' for cnl_id, prof_ids in not_found_prof_oids_dict])

            MailSender.send_email_async(
                f"User ID: {root_uid}"
                f""
                f"Connected channels but not found (`ObjectId`): "
                f"{' & '.join(not_found_channel)}"
                f""
                f"Connected profiles but not found (`ObjectId`): "
                f"{not_found_prof_oids_txt}",
                subject="Possible Data Corruption on Getting User Profile Connection"
            )

        return ret


_inst = PermissionManager()
