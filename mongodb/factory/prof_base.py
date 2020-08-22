"""
Profile-related data controllers.

:class:`ProfileDataManager` controls the profile data itself.

    - This class does not care about who has the profile.

    - This class cares the properties of a profile, such as name and color.

:class:`UserProfileManager` controls the connection between the profile data and the user.

    - This class does not care about the properties of a profile.

    - This class cares who has certain profile(s).

:class:`PermissionPromotionRecordHolder` controls the data related to permission promotion record.

    - This class should be used for all types of manipulation on permission promotion record.
"""
from typing import Optional, List, Dict, Set, Union

import pymongo
from bson import ObjectId

from pymongo import UpdateOne

from extutils.boolext import to_bool
from extutils.checker import arg_type_ensure
from flags import ProfilePermission, ProfilePermissionDefault, PermissionLevel
from models import (
    OID_KEY, ChannelConfigModel, ChannelProfileModel, ChannelProfileConnectionModel, PermissionPromotionRecordModel
)
from mongodb.factory import ChannelManager
from mongodb.factory.results import (
    WriteOutcome, GetOutcome, OperationOutcome, UpdateOutcome,
    GetPermissionProfileResult, CreateProfileResult
)
from mongodb.utils import ExtendedCursor
from strres.mongodb import Profile

from ._base import BaseCollection

__all__ = ("ProfileDataManager", "UserProfileManager", "PermissionPromotionRecordHolder",)

DB_NAME = "channel"


class _UserProfileManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "user"
    model_class = ChannelProfileConnectionModel

    def build_indexes(self):
        self.create_index(
            [(ChannelProfileConnectionModel.UserOid.key, pymongo.DESCENDING),
             (ChannelProfileConnectionModel.ChannelOid.key, pymongo.DESCENDING)],
            name="Profile Connection Identity",
            unique=True)

    @arg_type_ensure
    def user_attach_profile(self, channel_oid: ObjectId, root_uid: ObjectId,
                            profile_oids: Union[ObjectId, List[ObjectId]]) \
            -> OperationOutcome:
        """
        Attach a profile to a the user ``root_uid`` using the ID of the profile and return the update result.

        :param channel_oid: channel of the profile
        :param root_uid: user to be attached
        :param profile_oids: profile(s) to attach
        :return: attachment result
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
            model: ChannelProfileConnectionModel = self.find_one_casted(
                {OID_KEY: id_}, parse_cls=ChannelProfileConnectionModel)

            if not model:
                raise ValueError("`upserted_id` exists but no corresponding model found.")

            # If the channel profile connection is upserted (newly inserted), add the default starred value to it
            self.update_one(
                {OID_KEY: id_},
                {
                    "$set":
                        {
                            ChannelProfileConnectionModel.Starred.key:
                                ChannelProfileConnectionModel.Starred.default_value}
                }
            )
        else:
            model: ChannelProfileConnectionModel = self.find_one_casted(
                {ChannelProfileConnectionModel.UserOid.key: root_uid},
                parse_cls=ChannelProfileConnectionModel)

            if not model:
                raise ValueError("`Model` should exists because `upserted_id` not exists, "
                                 "however no corresponding model found.")

        return OperationOutcome.O_COMPLETED

    @arg_type_ensure
    def get_user_profile_conn(self, channel_oid: ObjectId, root_uid: ObjectId) \
            -> Optional[ChannelProfileConnectionModel]:
        """
        Get the :class:`ChannelProfileConnectionModel` of the specified user in the specified channel.

        :return: `ChannelProfileConnectionModel` if exists
        """
        return self.find_one_casted(
            {ChannelProfileConnectionModel.UserOid.key: root_uid,
             ChannelProfileConnectionModel.ChannelOid.key: channel_oid},
            parse_cls=ChannelProfileConnectionModel)

    def get_user_channel_profiles(self, root_uid: ObjectId, *, inside_only: bool = True) \
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

    def get_channel_prof_conn(self, channel_oid: Union[ObjectId, List[ObjectId]], *, available_only=True) \
            -> List[ChannelProfileConnectionModel]:
        if isinstance(channel_oid, ObjectId):
            channel_oid = [channel_oid]

        filter_ = {ChannelProfileConnectionModel.ChannelOid.key: {"$in": channel_oid}}

        if available_only:
            filter_[f"{ChannelProfileConnectionModel.ProfileOids.key}.0"] = {"$exists": True}

        return list(self.find_cursor_with_count(filter_, parse_cls=ChannelProfileConnectionModel))

    def get_users_exist_channel_dict(self, user_oids: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        """
        Get a :class:`dict` which for each element:

            key is each user listed in ``user_oids`` and

            value is the OIDs of the channel they are in.

        :param user_oids: list of users to be checked
        :return: a `dict` containing the information described above
        """
        k = "in_channel"
        ret = {}

        pipeline = [
            {"$match": {
                ChannelProfileConnectionModel.UserOid.key: {"$in": user_oids}
            }},
            {"$group": {
                "_id": "$" + ChannelProfileConnectionModel.UserOid.key,
                k: {
                    "$addToSet": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$" + ChannelProfileConnectionModel.ProfileOids.key}, 0]},
                            "then": "$" + ChannelProfileConnectionModel.ChannelOid.key,
                            "else": None
                        }
                    }
                }
            }}
        ]

        for d in self.aggregate(pipeline):
            ret[d[OID_KEY]] = {oid for oid in d[k] if oid is not None}

        return ret

    def get_available_connections(self) -> ExtendedCursor[ChannelProfileConnectionModel]:
        return self.find_cursor_with_count(
            {ChannelProfileConnectionModel.ProfileOids.key + ".0": {"$exists": True}},
            parse_cls=ChannelProfileConnectionModel)

    def get_profile_user_oids(self, profile_oid: ObjectId) -> Set[ObjectId]:
        # Using native MongoDB method to increase the performance
        return {mdl[ChannelProfileConnectionModel.UserOid.key]
                for mdl in self.find({ChannelProfileConnectionModel.ProfileOids.key: profile_oid})}

    def get_profiles_user_oids(self, profile_oids: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        """
        Get a dict which
            key is the profile OID
            value is the user who have the corresponding profile

        This method does **NOT** check if the profile actually exists or not.

        If a profile does not have any user having it, the corresponding return value will be an empty set `set()`.

        :param profile_oids: profile OIDs to be checked
        :return: a dict which the key is profile OIDs and value is user OIDs
        """
        k = "u"

        aggr = self.aggregate([
            {"$match": {ChannelProfileConnectionModel.ProfileOids.key: {"$in": profile_oids}}},
            {"$unwind": "$" + ChannelProfileConnectionModel.ProfileOids.key},
            {"$group": {
                OID_KEY: "$" + ChannelProfileConnectionModel.ProfileOids.key,
                k: {"$addToSet": "$" + ChannelProfileConnectionModel.UserOid.key}
            }}
        ])

        ret = {e[OID_KEY]: set(e[k]) for e in aggr if e[OID_KEY] in profile_oids}

        for poid in profile_oids:
            if poid not in ret:
                ret[poid] = set()

        return ret

    def get_user_profile_dict(self, channel_oid: ObjectId) -> Dict[ObjectId, Set[ObjectId]]:
        """
        Get a :class:`dict` which key is the user OID in the channel and value is the OIDs of the profile they have.

        :param channel_oid: channel to get the `dict`
        :return: a dict containing the channel member OIDs as the key and their profile OIDs as the value
        """
        uk = ChannelProfileConnectionModel.UserOid.key
        pk = ChannelProfileConnectionModel.ProfileOids.key

        crs = self.find({ChannelProfileConnectionModel.ChannelOid.key: channel_oid}, projection={uk: 1, pk: 1})

        ret = {}

        for entry in crs:
            ret[entry[uk]] = set(entry[pk])

        return ret

    @arg_type_ensure
    def is_user_in_channel(self, channel_oid: ObjectId, root_oid: ObjectId) -> bool:
        return self.count_documents(
            {ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
             ChannelProfileConnectionModel.UserOid.key: root_oid,
             ChannelProfileConnectionModel.ProfileOids.key + ".0": {"$exists": True}}) > 0

    def mark_unavailable(self, channel_oid: ObjectId, root_oid: ObjectId):
        self.update_one(
            {ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
             ChannelProfileConnectionModel.UserOid.key: root_oid},
            {"$set": {
                ChannelProfileConnectionModel.ProfileOids.key: ChannelProfileConnectionModel.ProfileOids.none_obj()}})

    def detach_profile(self, profile_oid: ObjectId, user_oid: Optional[ObjectId] = None) -> UpdateOutcome:
        filter_ = {ChannelProfileConnectionModel.ProfileOids.key: profile_oid}

        if user_oid:
            filter_[ChannelProfileConnectionModel.UserOid.key] = user_oid

        return self.update_many_outcome(
            filter_, {"$pull": {ChannelProfileConnectionModel.ProfileOids.key: profile_oid}})

    def change_star(self, channel_oid: ObjectId, root_oid: ObjectId, star: bool) -> bool:
        """
        Change the star mark of the channel for a user.

        :param channel_oid: channel to be changed the star mark
        :param root_oid: user of the channel to change the star mark
        :param star: new star status
        :return: star changed or not
        """
        return self.update_one(
            {
                ChannelProfileConnectionModel.ChannelOid.key: channel_oid,
                ChannelProfileConnectionModel.UserOid.key: root_oid
            },
            {
                "$set": {ChannelProfileConnectionModel.Starred.key: star}
            }
        ).modified_count > 0


class _ProfileDataManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "prof"
    model_class = ChannelProfileModel

    def build_indexes(self):
        self.create_index(
            [(ChannelProfileModel.ChannelOid.key, pymongo.DESCENDING),
             (ChannelProfileModel.Name.key, pymongo.ASCENDING)],
            name="Profile Identity", unique=True)

    def on_init_async(self):
        super().on_init_async()

        cmds = []
        cmds.extend(self._fill_new_permission())

        if cmds:
            self.bulk_write(cmds)

    def _fill_new_permission(self):
        cmds = []

        for perm_cat in ProfilePermission:
            perm_key = f"{ChannelProfileModel.Permission.key}.{perm_cat.code}"

            for data in self.find_cursor_with_count({perm_key: {"$exists": False}}, parse_cls=ChannelProfileModel):
                cmds.append(
                    UpdateOne(
                        {OID_KEY: data.id},
                        {"$set": {
                            perm_key:
                                perm_cat in ProfilePermissionDefault.get_overridden_permissions(data.permission_level)
                        }}
                    )
                )

        return cmds

    def _create_profile(self, channel_oid: ObjectId, **fk_param):
        return self.insert_one_data(ChannelOid=channel_oid, **fk_param)

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelProfileModel]:
        return self.find_one_casted({OID_KEY: profile_oid}, parse_cls=ChannelProfileModel)

    def get_profile_dict(self, profile_oid_list: List[ObjectId]) -> Dict[ObjectId, ChannelProfileModel]:
        return {model.id: model for model
                in self.find_cursor_with_count({OID_KEY: {"$in": profile_oid_list}}, parse_cls=ChannelProfileModel)}

    def get_profile_name(self, channel_oid: ObjectId, name: str) -> Optional[ChannelProfileModel]:
        return self.find_one_casted(
            {ChannelProfileModel.ChannelOid.key: channel_oid, ChannelProfileModel.Name.key: name.strip()},
            parse_cls=ChannelProfileModel)

    def get_channel_profiles(self, channel_oid: ObjectId, partial_keyword: Optional[str] = None) \
            -> ExtendedCursor[ChannelProfileModel]:
        filter_ = {ChannelProfileModel.ChannelOid.key: channel_oid}

        if partial_keyword:
            filter_[ChannelProfileModel.Name.key] = {"$regex": partial_keyword, "$options": "i"}

        return self.find_cursor_with_count(filter_, parse_cls=ChannelProfileModel).sort([(OID_KEY, pymongo.ASCENDING)])

    def get_default_profile(self, channel_oid: ObjectId) -> GetPermissionProfileResult:
        """
        Get the default profile of the channel.

        Creates a default profile for ``channel_oid`` and set it to the channel if not exists.

        :param channel_oid: channel to get the default profile
        :return: result of getting the default profile
        """
        ex = None

        cnl = ChannelManager.get_channel_oid(channel_oid)
        if not cnl:
            return GetPermissionProfileResult(GetOutcome.X_CHANNEL_NOT_FOUND, ex)

        try:
            prof_oid = cnl.config.default_profile_oid
        except AttributeError:
            return GetPermissionProfileResult(GetOutcome.X_CHANNEL_CONFIG_ERROR, ex)

        if not cnl.config.is_field_none("DefaultProfileOid"):
            perm_prof: ChannelProfileModel = self.find_one_casted({OID_KEY: prof_oid}, parse_cls=ChannelProfileModel)

            if perm_prof:
                return GetPermissionProfileResult(GetOutcome.O_CACHE_DB, ex, perm_prof)

        create_result = self.create_default_profile(channel_oid)

        return GetPermissionProfileResult(
            GetOutcome.O_ADDED if create_result.success else GetOutcome.X_DEFAULT_PROFILE_ERROR,
            ex, create_result.model)

    def get_attachable_profiles(self, channel_oid: ObjectId, *,
                                existing_permissions: Optional[Set[ProfilePermission]] = None,
                                highest_perm_lv: PermissionLevel = PermissionLevel.NORMAL) \
            -> ExtendedCursor[ChannelProfileModel]:
        """
        Get the current attachable profiles in the specific channel.

        The returned result will be filtered by

        - Highest permission level ``highest_perm_lv``

            Every profile that is equal or lower than this permission level be returned

        - Already owned permissions ``existing_permissions``

            Every profile that is granted **ALL** of these permissions will be returned

        If a profile has a higher permission level, but does not contain all of the ``existing_permissions``,
        it will still being returned.

        :param channel_oid: channel to find the attachable profiles
        :param existing_permissions: currently already owned permissions
        :param highest_perm_lv: highest permission level allowed
        :return: attachable profiles
        """
        if not existing_permissions:
            existing_permissions = set()

        filter_ = {ChannelProfileModel.ChannelOid.key: channel_oid}

        forbidden_permissions = []
        overridden_permissions = ProfilePermissionDefault.get_overridden_permissions(highest_perm_lv)

        for perm in ProfilePermission:
            if perm not in overridden_permissions and perm not in existing_permissions:
                forbidden_permissions.append(perm)

        for perm in forbidden_permissions:
            filter_[f"{ChannelProfileModel.Permission.key}.{perm.code}"] = False

        filter_[ChannelProfileModel.PermissionLevel.key] = {"$lte": highest_perm_lv}

        return self.find_cursor_with_count(filter_, parse_cls=ChannelProfileModel)

    def create_default_profile(self, channel_oid: ObjectId, *,
                               set_to_channel: bool = True, check_channel: bool = True) -> CreateProfileResult:
        if check_channel and not ChannelManager.get_channel_oid(channel_oid):
            return CreateProfileResult(WriteOutcome.X_CHANNEL_NOT_FOUND)

        result = self.create_profile(ChannelOid=channel_oid, Name=str(Profile.DEFAULT_PROFILE_NAME))

        if set_to_channel and result.outcome.is_inserted:
            set_result = ChannelManager.set_config(
                channel_oid, ChannelConfigModel.DefaultProfileOid.key, result.model.id)

            if not set_result.is_success:
                result.model = None
                result.outcome = WriteOutcome.X_ON_SET_CONFIG

        return result

    def create_profile(self, **fkwargs) -> CreateProfileResult:
        """
        Create a profile using ``fkargs`` where the key to construct the model is field key.

        :param fkwargs: `dict` to construct the profile
        """
        model, outcome, ex = self.insert_one_data(**fkwargs)

        return CreateProfileResult(outcome, ex, model)

    def create_profile_model(self, model: ChannelProfileModel) -> CreateProfileResult:
        """
        Create a profile.

        Insert the passed-in ``model`` into the database.

        :param model: `ChannelProfileModel` to be inserted.
        """
        outcome, ex = self.insert_one_model(model)

        return CreateProfileResult(outcome, ex, model)

    @arg_type_ensure
    def update_profile(self, profile_oid: ObjectId, **new_jkwargs) -> UpdateOutcome:
        """
        Update a profile using the data in ``new_jkwargs``
        which the key should be the json key of :class:`ChannelProfileModel`.

        ``new_jkwargs`` will be validated.

        Returns :class:`UpdateOutcome.O_PARTIAL_ARGS_REMOVED` if
            Some keys in ``new_jkwargs`` are not assigned in :class:`ChannelProfileModel` and successfully updated.

            These keys will be removed along with its values.

        Returns :class:`UpdateOutcome.O_PARTIAL_ARGS_INVALID` if
            Some values in ``new_jkwargs`` is invalid and successfully updated.

            These values will be removed along with its keys.

        Returns :class:`UpdateOutcome.X_NOT_EXECUTED` if
            ``new_jkwargs`` is empty after validation.

        If there are any additional keys and also some invalid values,
        :class:`UpdateOutcome.O_PARTIAL_ARGS_REMOVED` will be returned if successfully updated.

        :param profile_oid: OID of the profile to be updated
        :param new_jkwargs: data to be updated
        """
        outcome = None

        d = {}

        for jk, v in new_jkwargs.items():
            # Handling permission keys
            if ChannelProfileModel.Permission.key in jk:
                jk, code = jk.split(".", 2)

                try:
                    ProfilePermission.cast(code)
                except (TypeError, ValueError):
                    outcome = UpdateOutcome.O_PARTIAL_ARGS_INVALID

                d[f"{jk}.{code}"] = to_bool(v).to_bool()
                continue

            if jk in self.data_model.model_json_keys():
                fi = self.data_model.get_field_class_instance(self.data_model.json_key_to_field(jk))
                if fi.read_only:
                    return UpdateOutcome.X_UNEDITABLE

                if fi.is_value_valid(v):
                    d[jk] = v
                else:
                    outcome = UpdateOutcome.O_PARTIAL_ARGS_INVALID
            else:
                outcome = UpdateOutcome.O_PARTIAL_ARGS_REMOVED

        if not d:
            return UpdateOutcome.X_NOT_EXECUTED

        update_outcome = self.update_many_outcome({OID_KEY: profile_oid}, {"$set": d})

        if update_outcome == UpdateOutcome.O_UPDATED:
            return outcome or update_outcome
        else:
            return update_outcome

    def delete_profile(self, profile_oid: ObjectId) -> bool:
        return self.delete_one({OID_KEY: profile_oid}).deleted_count > 0

    @arg_type_ensure
    def is_name_available(self, channel_oid: ObjectId, name: str):
        name = name.strip()

        if not name:
            return False

        return self.count_documents({ChannelProfileModel.Name.key: name,
                                     ChannelProfileModel.ChannelOid.key: channel_oid}) == 0


class _PermissionPromotionRecordHolder(BaseCollection):
    database_name = DB_NAME
    collection_name = "promo"
    model_class = PermissionPromotionRecordModel


UserProfileManager = _UserProfileManager()
ProfileDataManager = _ProfileDataManager()
PermissionPromotionRecordHolder = _PermissionPromotionRecordHolder()
