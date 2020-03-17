from threading import Thread
from typing import Optional, List, Dict, Set, Union

import pymongo
from bson import ObjectId

from django.utils.translation import gettext_lazy as _
from pymongo import UpdateOne

from extutils.color import ColorFactory
from extutils.checker import param_type_ensure
from extutils.emailutils import MailSender
from flags import PermissionCategory, PermissionCategoryDefault, PermissionLevel
from mongodb.factory import ChannelManager
from mongodb.factory.results import WriteOutcome, GetOutcome, GetPermissionProfileResult, CreatePermissionProfileResult
from mongodb.utils import CursorWithCount
from models import (
    OID_KEY, ChannelConfigModel, ChannelProfileListEntry,
    ChannelProfileModel, ChannelProfileConnectionModel, PermissionPromotionRecordModel)

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

    def user_attach_profile(self, channel_oid: ObjectId, root_uid: ObjectId,
                            profile_oids: Union[ObjectId, List[ObjectId]]) \
            -> ChannelProfileConnectionModel:
        """
        Attach `ChannelPermissionProfileModel` and return the attached data.
        """
        id_ = self.update_one(
            {
                ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
                ChannelProfileConnectionModel.UserOid.key: root_uid
            },
            {"$addToSet": {
                ChannelProfileConnectionModel.ProfileOids.key:
                    {"$each": profile_oids} if isinstance(profile_oids, list) else profile_oids
            }},
            upsert=True).upserted_id

        if id_:
            # noinspection PyTypeChecker
            model: ChannelProfileConnectionModel = self.find_one_casted(
                {OID_KEY: id_}, parse_cls=ChannelProfileConnectionModel)

            if not model:
                raise ValueError("`upserted_id` exists but no corresponding model found.")
        else:
            # noinspection PyTypeChecker
            model: ChannelProfileConnectionModel = self.find_one_casted(
                {ChannelProfileConnectionModel.UserOid.key: root_uid},
                parse_cls=ChannelProfileConnectionModel)

            if not model:
                raise ValueError("`Model` should exists because `upserted_id` not exists, "
                                 "however no corresponding model found.")

        return model

    def user_attch_profiles(self, channel_oid: ObjectId, root_uid: ObjectId, profile_oids: List[ObjectId]):
        self.update_one({ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
                         ChannelProfileConnectionModel.UserOid.key: root_uid},
                        {"$addToSet": {ChannelProfileConnectionModel.ProfileOids.key: {"$each": profile_oids}}})

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

    def get_user_channel_profiles(self, root_uid: ObjectId, inside_only: bool = True) \
            -> List[ChannelProfileConnectionModel]:
        filter_ = {ChannelProfileConnectionModel.UserOid.key: root_uid}

        if inside_only:
            filter_[f"{ChannelProfileConnectionModel.ProfileOids.key}.0"] = {"$exists": True}

        return list(self.find_cursor_with_count(
            filter_,
            parse_cls=ChannelProfileConnectionModel
        ).sort(
            [
                (ChannelProfileConnectionModel.Starred.key, pymongo.DESCENDING),
                (ChannelProfileConnectionModel.Id.key, pymongo.DESCENDING)
            ]
        ))

    def get_channel_members(self, channel_oid: Union[ObjectId, List[ObjectId]], available_only=True) \
            -> List[ChannelProfileConnectionModel]:
        if isinstance(channel_oid, ObjectId):
            filter_ = {ChannelProfileConnectionModel.ChannelOid.key: {"$in": [channel_oid]}}
        else:
            filter_ = {ChannelProfileConnectionModel.ChannelOid.key: {"$in": channel_oid}}

        if available_only:
            filter_[f"{ChannelProfileConnectionModel.ProfileOids.key}.0"] = {"$exists": True}

        return list(self.find_cursor_with_count(filter_, parse_cls=ChannelProfileConnectionModel))

    def get_users_exist_channel_dict(self, user_oids: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        k = "in_channel"
        ret = {}

        pipeline = [
            {"$match": {
                ChannelProfileConnectionModel.UserOid.key: {"$in": user_oids},
                ChannelProfileConnectionModel.ProfileOids.key + ".0": {"$exists": True}
            }},
            {"$group": {
                "_id": "$" + ChannelProfileConnectionModel.UserOid.key,
                k: {"$addToSet": "$" + ChannelProfileConnectionModel.ChannelOid.key}
            }}
        ]

        for d in self.aggregate(pipeline):
            ret[d[OID_KEY]] = d[k]

        return ret

    def get_available_connections(self) -> CursorWithCount:
        return self.find_cursor_with_count(
            {ChannelProfileConnectionModel.ProfileOids.key + ".0": {"$exists": True}},
            parse_cls=ChannelProfileConnectionModel)

    def get_profile_user_oids(self, profile_oid: ObjectId) -> List[ObjectId]:
        return [mdl.user_oid for mdl
                in self.find_cursor_with_count(
                    {ChannelProfileConnectionModel.ProfileOids.key: profile_oid},
                    parse_cls=ChannelProfileConnectionModel)]

    def mark_unavailable(self, channel_oid: ObjectId, root_oid: ObjectId):
        self.update_one(
            {ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
             ChannelProfileConnectionModel.UserOid.key: root_oid},
            {"$set": {
                ChannelProfileConnectionModel.ProfileOids.key: ChannelProfileConnectionModel.ProfileOids.none_obj()}})

    def detach_profile(self, profile_oid: ObjectId, user_oid: Optional[ObjectId] = None) -> WriteOutcome:
        filter_ = {ChannelProfileConnectionModel.ProfileOids.key: profile_oid}

        if user_oid:
            filter_[ChannelProfileConnectionModel.UserOid.key] = user_oid

        return self.update_many_outcome(
            filter_, {"$pull": {ChannelProfileConnectionModel.ProfileOids.key: profile_oid}})

    def change_star(self, channel_oid: ObjectId, root_oid: ObjectId, star: bool) -> bool:
        return self.update_one(
            {
                ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
                ChannelProfileConnectionModel.UserOid.key: root_oid
            },
            {
                "$set": {ChannelProfileConnectionModel.Starred.key: star}
            }
        ).modified_count > 0


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

    def on_init_async(self):
        super().on_init_async()

        cmds = []

        for perm_cat in PermissionCategory:
            perm_key = f"{ChannelProfileModel.Permission.key}.{perm_cat.code}"

            for data in self.find_cursor_with_count({perm_key: {"$exists": False}}, parse_cls=ChannelProfileModel):
                cmds.append(
                    UpdateOne(
                        {OID_KEY: data.id},
                        {"$set": {
                            perm_key:
                                perm_cat in PermissionCategoryDefault.get_overridden_permissions(data.permission_level)
                        }}
                    )
                )

        if cmds:
            self.bulk_write(cmds)

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelProfileModel]:
        return self.find_one_casted({OID_KEY: profile_oid}, parse_cls=ChannelProfileModel)

    def get_profile_dict(self, profile_oid_list: List[ObjectId]) -> Dict[ObjectId, ChannelProfileModel]:
        return {model.id: model for model
                in self.find_cursor_with_count({OID_KEY: {"$in": profile_oid_list}}, parse_cls=ChannelProfileModel)}

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

    def get_attachable_profiles(
            self, channel_oid: ObjectId, existing_permissions: Set[PermissionCategory],
            highest_perm_lv: PermissionLevel) \
            -> CursorWithCount:
        filter_ = {ChannelProfileModel.ChannelOid.key: channel_oid}

        # noinspection PyTypeChecker
        limited_permissions = set(PermissionCategory) \
            .difference(PermissionCategoryDefault.get_overridden_permissions(highest_perm_lv)) \
            .difference(existing_permissions)
        for perm in limited_permissions:
            filter_[f"{ChannelProfileModel.Permission.key}.{perm.code}"] = False

        return self.find_cursor_with_count(filter_, parse_cls=ChannelProfileModel)

    def create_default_profile(self, channel_oid: ObjectId) -> CreatePermissionProfileResult:
        default_profile, outcome, ex = self._create_profile_(channel_oid, Name=_("Default Profile"))

        if outcome.is_inserted:
            set_success = ChannelManager.set_config(
                channel_oid, ChannelConfigModel.DefaultProfileOid.key, default_profile.id)

            if not set_success:
                outcome = WriteOutcome.X_ON_SET_CONFIG

        return CreatePermissionProfileResult(outcome, default_profile, ex)

    def create_profile(self, kwargs) -> CreatePermissionProfileResult:
        model, outcome, ex = self.insert_one_data(**kwargs)

        return CreatePermissionProfileResult(outcome, model, ex)

    def delete_profile(self, profile_oid: ObjectId):
        return self.delete_one({OID_KEY: profile_oid}).deleted_count > 0

    def _create_profile_(self, channel_oid: ObjectId, **fk_param):
        return self.insert_one_data(
            ChannelOid=channel_oid, **fk_param)

    @param_type_ensure
    def is_name_available(self, channel_oid: ObjectId, name: str):
        return self.count_documents({ChannelProfileModel.Name.key: name,
                                     ChannelProfileModel.ChannelOid.key: channel_oid}) == 0


class PermissionPromotionRecordHolder(BaseCollection):
    database_name = DB_NAME
    collection_name = "promo"
    model_class = PermissionPromotionRecordModel


class ProfileManager:
    def __init__(self):
        self._conn = UserProfileManager()
        self._prof = ProfileDataManager()
        self._promo = PermissionPromotionRecordHolder()

    @param_type_ensure
    def register_new_default_async(self, channel_oid: ObjectId, root_uid: ObjectId):
        Thread(target=self.register_new_default, args=(channel_oid, root_uid)).start()

    @param_type_ensure
    def register_new_default(self, channel_oid: ObjectId, root_uid: ObjectId):
        default_prof = self._prof.get_default_profile(channel_oid)
        if default_prof.success:
            self._conn.user_attach_profile(channel_oid, root_uid, default_prof.model.id)

    # Used for sanitizing webpage form data
    # noinspection PyMethodMayBeStatic
    def process_profile_kwargs(self, profile_kwargs: dict):
        # --- Collate `PermissionLevel`
        perm_lv = PermissionLevel.cast(profile_kwargs["PermissionLevel"])
        profile_kwargs["PermissionLevel"] = perm_lv

        # --- Collate `Permission`
        perm_dict = {}
        # Fill turned-on permissions
        for k, v in profile_kwargs.items():
            if k.startswith("Permission."):
                perm_dict[k[len("Permission."):]] = True
                del profile_kwargs[k]

        # Fill default overriden permissions by permission level
        for perm in PermissionCategoryDefault.get_overridden_permissions(perm_lv):
            perm_dict[perm.code_str] = True

        # Fill the rest of the permissions
        for perm_cat in PermissionCategory:
            if perm_cat.code_str not in perm_dict:
                perm_dict[perm_cat.code_str] = False

        profile_kwargs["Permission"] = perm_dict

        # --- Collate `Color`
        profile_kwargs["Color"] = ColorFactory.from_hex(profile_kwargs["Color"])

        return profile_kwargs

    # noinspection PyTypeChecker
    @param_type_ensure
    def register_new(self, root_uid: ObjectId, profile_kwargs: dict) -> Optional[ChannelProfileModel]:
        create_result = self._prof.create_profile(profile_kwargs)
        if create_result.success:
            self._conn.user_attach_profile(create_result.model.channel_oid, root_uid, create_result.model.id)

        return create_result.model

    @param_type_ensure
    def get_user_profiles(self, channel_oid: ObjectId, root_uid: ObjectId) -> List[ChannelProfileModel]:
        """
        Get the `list` of `ChannelProfileModel` of the specified user.

        :return: `None` on not found.
        """
        conn = self._conn.get_user_profile_conn(channel_oid, root_uid)

        if conn:
            ret = []
            for poid in conn.profile_oids:
                prof = self._prof.get_profile(poid)
                if prof:
                    ret.append(prof)

            return ret
        else:
            return []

    # noinspection PyMethodMayBeStatic
    def highest_permission_level(self, profiles: List[ChannelProfileModel]) -> PermissionLevel:
        current_max = PermissionLevel.lowest()

        for profile in profiles:
            if profile.permission_level > current_max:
                current_max = profile.permission_level

        return current_max

    def get_user_channel_profiles(self, root_uid: Optional[ObjectId], inside_only: bool = True,
                                  accessbible_only: bool = True) \
            -> List[ChannelProfileListEntry]:
        if root_uid is None:
            return []

        ret = []

        not_found_channel = []
        not_found_prof_oids_dict = {}

        channel_oid_list = []
        profile_oid_list = []
        prof_conns = []
        for d in self._conn.get_user_channel_profiles(root_uid, inside_only):
            channel_oid_list.append(d.channel_oid)
            profile_oid_list.extend(d.profile_oids)
            prof_conns.append(d)

        channel_dict = ChannelManager.get_channel_dict(channel_oid_list, accessbible_only=False)
        profile_dict = self._prof.get_profile_dict(profile_oid_list)

        for prof_conn in prof_conns:
            not_found_prof_oids = []

            # Get Channel Model
            cnl_oid = prof_conn.channel_oid
            cnl = channel_dict.get(cnl_oid)

            if cnl is None:
                not_found_channel.append(cnl_oid)
                continue
            elif accessbible_only and not cnl.bot_accessible:
                continue

            default_profile_oid = cnl.config.default_profile_oid

            # Get Profile Model
            prof = []
            for p in prof_conn.profile_oids:
                pm = profile_dict.get(p)
                if pm:
                    prof.append(pm)
                else:
                    not_found_prof_oids.append(p)

            if len(prof) == 0:
                not_found_prof_oids_dict[cnl_oid] = []
            elif len(not_found_prof_oids) > 0:
                not_found_prof_oids_dict[cnl_oid] = not_found_prof_oids
            else:
                perms = self.get_permissions(prof)
                can_ced_profile = self.can_ced_profile(perms)

                ret.append(
                    ChannelProfileListEntry(
                        channel_data=cnl, channel_name=cnl.get_channel_name(root_uid), profiles=prof,
                        starred=prof_conn.starred, default_profile_oid=default_profile_oid,
                        can_ced_profile=can_ced_profile
                    ))

        if len(not_found_channel) > 0 or len(not_found_prof_oids_dict) > 0:
            not_found_prof_oids_txt = "\n".join(
                [f'{cnl_id}: {" / ".join([str(oid) for oid in prof_ids])}'
                 for cnl_id, prof_ids in not_found_prof_oids_dict.items()])

            MailSender.send_email_async(
                f"User ID: <code>{root_uid}</code><hr>"
                f"Channel IDs not found in DB:<br>"
                f"<pre>{' & '.join([str(c) for c in not_found_channel])}</pre><hr>"
                f"Profile IDs not found in DB:<br>"
                f"<pre>{not_found_prof_oids_txt}</pre>",
                subject="Possible Data Corruption on Getting User Profile Connection"
            )

        return sorted(ret, key=lambda item: item.channel_data.bot_accessible, reverse=True)

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelProfileModel]:
        return self._prof.get_profile(profile_oid)

    def get_users_exist_channel_dict(self, user_oids: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        return self._conn.get_users_exist_channel_dict(user_oids)

    # noinspection PyMethodMayBeStatic
    def get_permissions(self, profiles: List[ChannelProfileModel]) -> Set[PermissionCategory]:
        ret = set()

        for prof in profiles:
            for perm_cat, perm_grant in prof.permission.items():
                perm = PermissionCategory.cast(perm_cat, silent_fail=True)
                if perm_grant and perm:
                    ret.add(perm)

            highest_perm_lv = self.highest_permission_level(profiles)
            ret = ret.union(PermissionCategoryDefault.get_overridden_permissions(highest_perm_lv))

        return ret

    # noinspection PyMethodMayBeStatic
    def get_user_permissions(self, channel_oid: ObjectId, root_uid: ObjectId) -> Set[PermissionCategory]:
        return self.get_permissions(self.get_user_profiles(channel_oid, root_uid))

    def get_channel_members(self, channel_oid: Union[ObjectId, List[ObjectId]], available_only=False) \
            -> List[ChannelProfileConnectionModel]:
        return self._conn.get_channel_members(channel_oid, available_only)

    def get_available_connections(self) -> CursorWithCount:
        return self._conn.get_available_connections()

    def get_attachable_profiles(self, channel_oid: ObjectId, root_uid: ObjectId) -> List[ChannelProfileModel]:
        profiles = self.get_user_profiles(channel_oid, root_uid)
        exist_perm = self.get_permissions(profiles)
        highest_perm = self.highest_permission_level(profiles)
        attachables = {prof.id: prof
                       for prof in self._prof.get_attachable_profiles(channel_oid, exist_perm, highest_perm)}

        # Remove default profile
        channel_data = ChannelManager.get_channel_oid(channel_oid)
        del attachables[channel_data.config.default_profile_oid]

        return list(attachables.values())

    def get_profile_user_oids(self, profile_oid: ObjectId) -> List[ObjectId]:
        return self._conn.get_profile_user_oids(profile_oid)

    def is_name_available(self, channel_oid: ObjectId, name: str):
        return self._prof.is_name_available(channel_oid, name)

    # noinspection PyMethodMayBeStatic
    def can_ced_profile(self, permissions: Set[PermissionCategory]):
        """CED Stands for Create / Edit / Delete."""
        return PermissionCategory.PRF_CED in permissions

    # noinspection PyMethodMayBeStatic
    def can_control_profile_member(self, permissions: Set[PermissionCategory]):
        return PermissionCategory.PRF_CONTROL_MEMBER in permissions

    def mark_unavailable_async(self, channel_oid: ObjectId, root_oid: ObjectId):
        Thread(target=self._conn.mark_unavailable, args=(channel_oid, root_oid)).start()

    def change_channel_star(self, channel_oid: ObjectId, root_oid: ObjectId, star: bool) -> bool:
        return self._conn.change_star(channel_oid, root_oid, star)

    @param_type_ensure
    def attach_profile(self, user_oid: ObjectId, channel_oid: ObjectId, profile_oid: ObjectId) \
            -> ChannelProfileConnectionModel:
        return self._conn.user_attach_profile(channel_oid, user_oid, profile_oid)

    def detach_profile(self, profile_oid: ObjectId, user_oid: Optional[ObjectId] = None) -> WriteOutcome:
        """Detach the profile from all users if `user_oid` is `None`."""
        return self._conn.detach_profile(profile_oid, user_oid)

    def delete_profile(self, profile_oid: ObjectId) -> bool:
        """Returns if there's an item deleted."""
        return self._prof.delete_profile(profile_oid)


_inst = ProfileManager()
