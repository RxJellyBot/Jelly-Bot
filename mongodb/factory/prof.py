from typing import Optional, List

import pymongo
from bson import ObjectId

from django.utils.translation import gettext_lazy as _

from extutils.checker import param_type_ensure
from extutils.emailutils import MailSender
from flags import PermissionCategory, PermissionCategoryDefault
from mongodb.factory import ChannelManager
from mongodb.factory.results import WriteOutcome, GetOutcome, GetPermissionProfileResult, CreatePermissionProfileResult
from mongodb.utils import CheckableCursor
from models import (
    OID_KEY, ChannelConfigModel, ChannelProfileListEntry,
    ChannelProfileModel, ChannelProfileConnectionModel, PermissionPromotionRecordModel
)

from ._base import BaseCollection

DB_NAME = "channel"


class UserProfileManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "user"
    model_class = ChannelProfileConnectionModel

    def __init__(self):
        super().__init__()
        self.create_index(
            [(ChannelProfileConnectionModel.UserOid.key, pymongo.DESCENDING),
             (ChannelProfileConnectionModel.ChannelOid.key, pymongo.DESCENDING)],
            name="Profile Connection Identity",
            unique=True)

    def user_attach_profile(self, channel_oid: ObjectId, root_uid: ObjectId, profile_oid: ObjectId) \
            -> ChannelProfileConnectionModel:
        """
        Attach `ChannelPermissionProfileModel` and return the attached data.
        """
        id_ = self.update_one(
            {ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
             ChannelProfileConnectionModel.UserOid.key: root_uid},
            {"$addToSet": {ChannelProfileConnectionModel.ProfileOids.key: profile_oid}}, upsert=True).upserted_id

        if id_:
            model = self.find_one_casted(
                {OID_KEY: id_}, parse_cls=ChannelProfileConnectionModel)

            if not model:
                raise ValueError("`upserted_id` exists but no corresponding model found.")
        else:
            model = self.find_one_casted(
                {ChannelProfileConnectionModel.UserOid.key: root_uid},
                parse_cls=ChannelProfileConnectionModel)

            if not model:
                raise ValueError("`Model` should exists because `upserted_id` not exists, "
                                 "however no corresponding model found.")

        return model

    # INCOMPLETE: user_detach_profile and delete

    def get_user_profile_conn(self, channel_oid: ObjectId, root_uid: ObjectId) \
            -> Optional[ChannelProfileConnectionModel]:
        """
        Get the `ChannelProfileConnectionModel` of the specified user in the specified channel.

        :return: `None` if not found.
        """

        if channel_oid and root_uid:
            return self.find_one_casted(
                {ChannelProfileConnectionModel.UserOid.key: root_uid,
                 ChannelProfileConnectionModel.ChannelOid.key: channel_oid},
                parse_cls=ChannelProfileConnectionModel)
        else:
            return None

    def get_user_channel_profiles(self, root_uid: ObjectId) -> CheckableCursor:
        return self.find_checkable_cursor(
            {ChannelProfileConnectionModel.UserOid.key: root_uid},
            parse_cls=ChannelProfileConnectionModel)


class ProfileDataManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "prof"
    model_class = ChannelProfileModel

    def __init__(self):
        super().__init__()
        self.create_index(
            [(ChannelProfileModel.ChannelOid.key, pymongo.DESCENDING),
             (ChannelProfileModel.Name.key, pymongo.ASCENDING)],
            name="Profile Identity", unique=True)

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelProfileModel]:
        return self.find_one_casted({OID_KEY: profile_oid}, parse_cls=ChannelProfileModel)

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
            perm_prof = self.find_one_casted({OID_KEY: prof_oid}, parse_cls=ChannelProfileModel)

            if perm_prof:
                return GetPermissionProfileResult(GetOutcome.O_CACHE_DB, perm_prof, ex)

        create_result = self.create_default_profile(channel_oid)

        return GetPermissionProfileResult(
            GetOutcome.O_ADDED if create_result.success else GetOutcome.X_DEFAULT_PROFILE_ERROR,
            create_result.model, ex)

    def create_default_profile(self, channel_oid: ObjectId) -> CreatePermissionProfileResult:
        default_profile, outcome, ex, insert_result = self._create_profile_(channel_oid, Name=_("Default Profile"))

        if outcome.is_success:
            set_success = ChannelManager.set_config(
                channel_oid, ChannelConfigModel.DefaultProfileOid.key, default_profile.id)

            if not set_success:
                outcome = WriteOutcome.X_ON_SET_CONFIG

        return CreatePermissionProfileResult(outcome, default_profile, ex)

    def _create_profile_(self, channel_oid: ObjectId, **fk_param):
        return self.insert_one_data(
            ChannelProfileModel, ChannelOid=channel_oid, **fk_param)

    # INCOMPLETE: Profile/Permission - Ensure mod/admin promotable if the mod/admin to be demoted is the last
    # INCOMPLETE: Profile/Permission -
    #  Custom permission profile creation (name and color changable only) - create then change
    pass


class PermissionPromotionRecordHolder(BaseCollection):
    database_name = DB_NAME
    collection_name = "promo"
    model_class = PermissionPromotionRecordModel

    # INCOMPLETE: Permission/Promotion - Keeps the promo record for a short period
    # INCOMPLETE: Promote for any role who needs promotion or direct assignment
    pass


class ProfileManager:
    def __init__(self):
        self._conn = UserProfileManager()
        self._prof = ProfileDataManager()
        self._promo = PermissionPromotionRecordHolder()

    def register_new_default(self, channel_oid: ObjectId, root_uid: ObjectId):
        default_prof = self._prof.get_default_profile(channel_oid)
        if default_prof.success:
            self._conn.user_attach_profile(channel_oid, root_uid, default_prof.model.id)

    @param_type_ensure
    def get_user_profiles(self, channel_oid: ObjectId, root_uid: ObjectId) -> List[ChannelProfileModel]:
        """
        Get the `list` of `ChannelProfileModel` of the specified user.

        :return: `None` on not found.
        """
        conn = self._conn.get_user_profile_conn(channel_oid, root_uid)

        if conn:
            return [self._prof.get_profile(poid)
                    for poid
                    in conn.profile_oids if not None]
        else:
            return []

    def get_user_channel_profiles(self, root_uid: Optional[ObjectId]) -> List[ChannelProfileListEntry]:
        if root_uid is None:
            return []

        ret = []

        not_found_channel = []
        not_found_prof_oids_dict = {}

        crs = self._conn.get_user_channel_profiles(root_uid)

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
                pm = self._prof.get_profile(p)
                if pm:
                    prof.append(pm)
                else:
                    not_found_prof_oids.append(p)

            if len(prof) == 0:
                not_found_prof_oids_dict[d.channel_oid] = []
            elif len(not_found_prof_oids) > 0:
                not_found_prof_oids_dict[d.channel_oid] = not_found_prof_oids
            else:
                ret.append(ChannelProfileListEntry(channel=cnl, profiles=prof))

        if len(not_found_channel) > 0 or len(not_found_prof_oids_dict) > 0:
            not_found_prof_oids_txt = "\n".join(
                [f'{cnl_id}: {" / ".join(prof_ids)}' for cnl_id, prof_ids in not_found_prof_oids_dict])

            MailSender.send_email_async(
                f"User ID: <code>{root_uid}</code><hr>"
                f"Channel IDs not found in DB:<br>"
                f"<pre>{' & '.join([str(c) for c in not_found_channel])}</pre><hr>"
                f"Profile IDs not found in DB:<br>"
                f"<pre>{not_found_prof_oids_txt}</pre>",
                subject="Possible Data Corruption on Getting User Profile Connection"
            )

        return ret

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelProfileModel]:
        return self._prof.get_profile(profile_oid)

    # noinspection PyMethodMayBeStatic
    def get_permissions(self, profiles: List[ChannelProfileModel]) -> List[PermissionCategory]:
        ret = []

        for prof in profiles:
            ret.extend([PermissionCategory.cast(perm_cat)
                        for perm_cat, perm_grant
                        in prof.permission.items() if perm_grant])

            if prof.is_mod:
                ret.extend(PermissionCategory.cast(perm_cat)
                           for perm_cat, perm_grant
                           in PermissionCategoryDefault.get_mod_override() if perm_grant)

            if prof.is_admin:
                ret.extend(PermissionCategory.cast(perm_cat)
                           for perm_cat, perm_grant
                           in PermissionCategoryDefault.get_admin_override() if perm_grant)

        return ret


_inst = ProfileManager()
