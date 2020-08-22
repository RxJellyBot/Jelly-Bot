"""
Profile-related data controllers.

:class:`ProfileManager` is the main class to control profiles.

    - Any controls besides tests should use this class to manipulate the profile data.

:class:`ProfileDataManager` controls the profile data itself.

    - This class does not care about who has the profile.

    - This class cares the properties of a profile, such as name and color.

:class:`UserProfileManager` controls the connection between the profile data and the user.

    - This class does not care about the properties of a profile.

    - This class cares who has certain profile(s).
"""
from threading import Thread
from typing import Optional, List, Dict, Set, Union

import pymongo
from bson import ObjectId

from pymongo import UpdateOne

from env_var import is_testing
from extutils.boolext import to_bool
from extutils.color import ColorFactory
from extutils.checker import arg_type_ensure
from extutils.emailutils import MailSender
from flags import ProfilePermission, ProfilePermissionDefault, PermissionLevel
from mixin import ClearableMixin
from models import (
    OID_KEY, ChannelConfigModel, ChannelProfileListEntry,
    ChannelProfileModel, ChannelProfileConnectionModel, PermissionPromotionRecordModel
)
from models.exceptions import ModelConstructionError, RequiredKeyNotFilledError, InvalidModelFieldError
from mongodb.factory import ChannelManager
from mongodb.factory.results import (
    WriteOutcome, GetOutcome, OperationOutcome, UpdateOutcome,
    GetPermissionProfileResult, CreateProfileResult, RegisterProfileResult, ArgumentParseResult
)
from mongodb.utils import ExtendedCursor
from strres.mongodb import Profile

from ._base import BaseCollection

__all__ = ("ProfileManager", "ProfileDataManager", "UserProfileManager", "PermissionPromotionRecordHolder",)

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


class _ProfileManager(ClearableMixin):
    @staticmethod
    def _create_kwargs_channel_oid(ret_kwargs, profile_fkwargs):
        fk_coid = ChannelProfileModel.json_key_to_field(ChannelProfileModel.ChannelOid.key)
        if fk_coid not in profile_fkwargs:
            return ArgumentParseResult(OperationOutcome.X_MISSING_CHANNEL_OID)

        try:
            coid = ObjectId(profile_fkwargs[fk_coid])
        except Exception as e:
            return ArgumentParseResult(OperationOutcome.X_INVALID_CHANNEL_OID, e)

        ret_kwargs[fk_coid] = coid
        return None

    @staticmethod
    def _create_kwargs_perm_lv(ret_kwargs, profile_fkwargs):
        fk_perm_lv = ChannelProfileModel.json_key_to_field(ChannelProfileModel.PermissionLevel.key)
        if fk_perm_lv not in profile_fkwargs:
            return None

        try:
            perm_lv = PermissionLevel.cast(profile_fkwargs[fk_perm_lv])
        except (TypeError, ValueError) as e:
            return ArgumentParseResult(OperationOutcome.X_INVALID_PERM_LV, e)

        ret_kwargs[fk_perm_lv] = perm_lv
        return None

    @staticmethod
    def _create_kwargs_permission(ret_kwargs, profile_fkwargs):
        fk_perm = ChannelProfileModel.json_key_to_field(ChannelProfileModel.Permission.key)
        fk_perm_initial = f"{fk_perm}."
        perm_dict = {}
        keys_to_remove = set()

        # Fill turned-on permissions
        for fk, v in profile_fkwargs.items():
            if fk.startswith(fk_perm_initial):
                perm_dict[fk[len(fk_perm_initial):]] = True
                keys_to_remove.add(fk)

        # Remove `Permission` in `profile_fkwargs` or the program will misjudge the status of the args
        # and return `OperationOutcome.O_ADDL_ARGS_OMITTED`.
        for k in keys_to_remove:
            del profile_fkwargs[k]

        fk_perm_lv = ChannelProfileModel.json_key_to_field(ChannelProfileModel.PermissionLevel.key)
        # Fill default overridden permissions by permission level
        if fk_perm_lv in ret_kwargs:
            for perm in ProfilePermissionDefault.get_overridden_permissions(ret_kwargs[fk_perm_lv]):
                perm_dict[perm.code_str] = True

        # Fill the rest of the permissions
        for perm_cat in ProfilePermission:
            if perm_cat.code_str not in perm_dict:
                perm_dict[perm_cat.code_str] = False

        if perm_dict:
            ret_kwargs[fk_perm] = perm_dict

        return None

    @staticmethod
    def _create_kwargs_color(ret_kwargs, profile_fkwargs):
        fk_color = ChannelProfileModel.json_key_to_field(ChannelProfileModel.Color.key)
        if fk_color not in profile_fkwargs:
            return None

        try:
            color = ColorFactory.from_hex(profile_fkwargs[fk_color])
        except ValueError as e:
            return ArgumentParseResult(OperationOutcome.X_INVALID_COLOR, e)

        ret_kwargs[fk_color] = color
        return None

    @staticmethod
    def _create_kwargs_other(ret_kwargs, profile_fkwargs):
        args_not_collated = set(profile_fkwargs) - set(ret_kwargs)
        if args_not_collated:
            for fk in args_not_collated:
                if fk not in ChannelProfileModel.model_field_keys():
                    continue

                fi = ChannelProfileModel.get_field_class_instance(fk)
                if not fi:
                    continue

                val = profile_fkwargs[fk]
                if not fi.is_type_matched(val):
                    return ArgumentParseResult(OperationOutcome.X_VALUE_TYPE_MISMATCH)
                if not fi.is_value_valid(val):
                    return ArgumentParseResult(OperationOutcome.X_VALUE_INVALID)

                ret_kwargs[fk] = fi.cast_to_desired_type(val)

        if set(profile_fkwargs) - set(ret_kwargs):
            return ArgumentParseResult(OperationOutcome.O_ADDL_ARGS_OMITTED, parsed_args=ret_kwargs)

        if not ret_kwargs:
            return ArgumentParseResult(OperationOutcome.X_EMPTY_ARGS)

        return ArgumentParseResult(OperationOutcome.O_COMPLETED, parsed_args=ret_kwargs)

    @classmethod
    def process_create_profile_kwargs(cls, profile_fkwargs: dict) -> ArgumentParseResult:
        """
        Sanitizes and collates the data passed from the profile creation form of its corresponding webpage.

        After processing, it returns a ``dict`` with field keys
        which can be used to create a :class:`ChannelProfileModel`.

        :param profile_fkwargs: `dict` to be processed which the key os field key
        :return: `dict` with field keys to create a `ChannelProfileModel`
        """
        ret_kwargs = {}

        collate_result = cls._create_kwargs_channel_oid(ret_kwargs, profile_fkwargs)
        if collate_result:
            return collate_result

        collate_result = cls._create_kwargs_perm_lv(ret_kwargs, profile_fkwargs)
        if collate_result:
            return collate_result

        cls._create_kwargs_permission(ret_kwargs, profile_fkwargs)

        collate_result = cls._create_kwargs_color(ret_kwargs, profile_fkwargs)
        if collate_result:
            return collate_result

        return cls._create_kwargs_other(ret_kwargs, profile_fkwargs)

    @staticmethod
    def _edit_kwargs_permission_keys(fk, v, ret_kwargs):
        # Return if the code is accepted
        fk, code = fk.split(".", 2)
        jk = ChannelProfileModel.field_to_json_key(fk)

        try:
            ProfilePermission.cast(code)
            ret_kwargs[f"{jk}.{code}"] = to_bool(v).to_bool()
        except (TypeError, ValueError):
            return True

        return False

    @classmethod
    def process_edit_profile_kwargs(cls, profile_fkwargs: dict) -> ArgumentParseResult:
        """
        Sanitizes and collates the data passed from the profile edition form of its corresponding webpage.

        Returns a ``dict`` with json keys to be used as the MongoDB operand of ``$set``.

        :param profile_fkwargs: `dict` to be processed
        :return: `dict` with json keys to be used as the MongoDB operand of `$set`
        """
        contains_readonly = False
        contains_addl = False
        ret_kwargs = {}

        fk_perm = ChannelProfileModel.json_key_to_field(ChannelProfileModel.Permission.key)
        fk_perm_initial = f"{fk_perm}."

        for fk, v in profile_fkwargs.items():
            # Handling permission keys
            if fk.startswith(fk_perm_initial):
                contains_addl = cls._edit_kwargs_permission_keys(fk, v, ret_kwargs) or contains_addl
                continue

            # Handle other parameters
            jk = ChannelProfileModel.field_to_json_key(fk)
            f = ChannelProfileModel.get_field_class_instance(fk)

            if not jk or not f:
                contains_addl = True
                continue

            if f.read_only:
                contains_readonly = True
                continue

            if not f.is_type_matched(v):
                return ArgumentParseResult(OperationOutcome.X_VALUE_TYPE_MISMATCH)
            if not f.is_value_valid(v):
                return ArgumentParseResult(OperationOutcome.X_VALUE_INVALID)

            ret_kwargs[jk] = f.cast_to_desired_type(v)

        if contains_readonly:
            outcome = OperationOutcome.O_READONLY_ARGS_OMITTED
        elif contains_addl:
            outcome = OperationOutcome.O_ADDL_ARGS_OMITTED
        else:
            outcome = OperationOutcome.O_COMPLETED
        return ArgumentParseResult(outcome, parsed_args=ret_kwargs)

    def __init__(self):
        self._conn = _UserProfileManager()
        self._prof = _ProfileDataManager()
        self._promo = _PermissionPromotionRecordHolder()

    def clear(self):
        self._conn.clear()
        self._prof.clear()
        self._promo.clear()

    def _profile_modification_allowed(self, channel_oid: ObjectId, user_oid: ObjectId,
                                      target_oid: Optional[ObjectId]) \
            -> bool:
        """
        Check if the user with ``user_oid`` has the permission to perform profile modification.

        If ``target_oid`` is ``None``, the method will consider that the modification will be performed on others.

        :param channel_oid: channel OID of the profile
        :param user_oid: user to execute the profile modification
        :param target_oid: the user to be performed the profile modification
        :return: if the profile modification is allowed
        """
        permissions = self.get_user_permissions(channel_oid, user_oid)

        # No permissions available means the user is not in the channel
        if not permissions:
            return False

        if not target_oid or user_oid != target_oid:
            return ProfilePermission.PRF_CONTROL_MEMBER in permissions
        else:
            return ProfilePermission.PRF_CONTROL_SELF in permissions

    def create_default_profile(self, channel_oid: ObjectId, *,
                               set_to_channel: bool = True, check_channel: bool = True) \
            -> CreateProfileResult:
        """
        Create a default profile for ``channel_oid`` and set it to the channel if ``set_to_channel`` is ``True``.

        Note that if ``set_to_channel`` is ``True``, ``check_channel`` is ``False`` and the channel does not exist,
        :class:`WriteOutcome.X_ON_SET_CONFIG` will be the outcome in the result.

        :param channel_oid: channel to get the default profile
        :param set_to_channel: if the created profile should be set to the channel
        :param check_channel: check if the channel is registered
        :return: result of creating the default profile
        """
        return self._prof.create_default_profile(
            channel_oid, set_to_channel=set_to_channel, check_channel=check_channel)

    @arg_type_ensure
    def register_new(self, root_uid: ObjectId, parsed_args: Optional[ArgumentParseResult] = None, **profile_fkwargs) \
            -> RegisterProfileResult:
        """
        Register a new profile and attach it to the user if success.

        The keys of ``profile_kwargs`` is field key.

        If both ``parsed_args`` and ``profile_kwargs`` is present, ``profile_kwargs`` will be ignored.

        :param root_uid: user's OID
        :param parsed_args: parsed argument result body
        :param profile_fkwargs: arguments to construct a profile
        :return: newly constructed model
        """
        parse_arg_outcome = None
        if parsed_args:
            if not parsed_args.success:
                return RegisterProfileResult(WriteOutcome.X_NOT_EXECUTED, parse_arg_outcome=parsed_args.outcome)

            kwargs = parsed_args.parsed_args
            parse_arg_outcome = parsed_args.outcome
        else:
            kwargs = profile_fkwargs

        try:
            prof_model = ChannelProfileModel(**kwargs)
        except RequiredKeyNotFilledError as ex:
            return RegisterProfileResult(WriteOutcome.X_REQUIRED_NOT_FILLED, ex)
        except InvalidModelFieldError as ex:
            return RegisterProfileResult(WriteOutcome.X_TYPE_MISMATCH, ex)
        except ModelConstructionError as ex:
            return RegisterProfileResult(WriteOutcome.X_INVALID_MODEL, ex)

        reg_result = self.register_new_model(root_uid, prof_model)

        return RegisterProfileResult(
            reg_result.outcome, reg_result.exception, reg_result.model, reg_result.attach_outcome, parse_arg_outcome)

    @arg_type_ensure
    def register_new_default(self, channel_oid: ObjectId, root_uid: ObjectId) -> RegisterProfileResult:
        attach_outcome = OperationOutcome.X_NOT_EXECUTED
        prof_result = self._prof.get_default_profile(channel_oid)

        if prof_result.success:
            attach_outcome = self._conn.user_attach_profile(channel_oid, root_uid, prof_result.model.id)

        return RegisterProfileResult(prof_result.outcome, prof_result.exception, prof_result.model, attach_outcome)

    def register_new_default_async(self, channel_oid: ObjectId, root_uid: ObjectId):
        if is_testing():
            # No async if testing
            self.register_new_default(channel_oid, root_uid)
        else:
            Thread(target=self.register_new_default, args=(channel_oid, root_uid)).start()

    @arg_type_ensure
    def register_new_model(self, root_uid: ObjectId, model: ChannelProfileModel) -> RegisterProfileResult:
        """
        Register a new profile with the user's oid and the constructed :class:`ChannelProfileModel`.

        :param root_uid: OID of the user to attach the profile
        :param model: profile model to be inserted
        :return: profile registration result
        """
        attach_outcome = OperationOutcome.X_NOT_EXECUTED

        if model.permission_set \
                - self.get_user_permissions(model.channel_oid, root_uid) \
                - ProfilePermissionDefault.get_overridden_permissions(model.permission_level):
            return RegisterProfileResult(WriteOutcome.X_INSUFFICIENT_PERMISSION)

        create_result = self._prof.create_profile_model(model)
        if create_result.success:
            attach_outcome = self._conn.user_attach_profile(
                create_result.model.channel_oid, root_uid, create_result.model.id)

        return RegisterProfileResult(
            create_result.outcome, create_result.exception, create_result.model, attach_outcome)

    def update_profile(self, channel_oid: ObjectId, root_oid: ObjectId, profile_oid: ObjectId,
                       parsed_args: Optional[ArgumentParseResult] = None, **update_dict) \
            -> UpdateOutcome:
        """
        Update the profile.

        If ``parsed_args`` is provided, and the parsing outcome is success,
        contents of ``update_dict`` will be omitted.

        :param channel_oid: OID of the channel of the profile
        :param root_oid: OID of the user performing this update
        :param profile_oid: OID of the profile to be updated
        :param parsed_args: result body of the parsed update arguments
        :param update_dict: unparsed kwargs with json key to be used with MongoDB operator `$set`
        :return: outcome of the update
        """
        if parsed_args:
            if not parsed_args.success:
                return UpdateOutcome.X_ARGS_PARSE_FAILED

            update_dict = parsed_args.parsed_args

        # Check permissions
        perms = {ProfilePermission.cast(k.split(".", 2)[1]) for k, v in update_dict.items()
                 if k.startswith(ChannelProfileModel.Permission.key) and to_bool(v).to_bool()}
        if perms and perms - self.get_user_permissions(channel_oid, root_oid):
            return UpdateOutcome.X_INSUFFICIENT_PERMISSION

        return self._prof.update_profile(profile_oid, **update_dict)

    def update_channel_star(self, channel_oid: ObjectId, root_oid: ObjectId, star: bool) -> bool:
        """
        Change the star mark of the channel for a user.

        :param channel_oid: channel to be changed the star mark
        :param root_oid: user of the channel to change the star mark
        :param star: new star status
        :return: star changed or not
        """
        return self._conn.change_star(channel_oid, root_oid, star)

    @arg_type_ensure
    def attach_profile_name(self, channel_oid: ObjectId, user_oid: ObjectId, profile_name: str,
                            target_oid: Optional[ObjectId] = None) \
            -> OperationOutcome:
        """
        Attach profile to the target by providing the exact profile name.

        If ``target_oid`` is ``None``, then the profile will be attached to self (``user_oid``).

        :param channel_oid: channel of the profile
        :param user_oid: user executing this action
        :param profile_name: full name of the profile to be attached
        :param target_oid: profile attaching target
        """
        prof = self.get_profile_name(channel_oid, profile_name)
        if not prof:
            return OperationOutcome.X_PROFILE_NOT_FOUND_NAME

        return self.attach_profile(channel_oid, user_oid, prof.id, target_oid, bypass_existence_check=True)

    @arg_type_ensure
    def attach_profile(self, channel_oid: ObjectId, user_oid: ObjectId, profile_oid: ObjectId,
                       target_oid: Optional[ObjectId] = None, *,
                       bypass_existence_check: bool = False) \
            -> OperationOutcome:
        """
        Attach profile to the target by providing the profile OID.

        If ``target_oid`` is ``None``, then the profile will be attached to self (``user_oid``).

        :param channel_oid: channel of the profile
        :param user_oid: user executing this action
        :param profile_oid: OID of the profile to be attached
        :param target_oid: profile attaching target
        :param bypass_existence_check: bypass the profile existence check
        """
        # --- Check target

        if not target_oid:
            target_oid = user_oid

        if not self._conn.is_user_in_channel(channel_oid, user_oid):
            return OperationOutcome.X_EXECUTOR_NOT_IN_CHANNEL

        if not self._conn.is_user_in_channel(channel_oid, target_oid):
            return OperationOutcome.X_TARGET_NOT_IN_CHANNEL

        # --- Check profile existence

        if not bypass_existence_check and not self.get_profile(profile_oid):
            return OperationOutcome.X_PROFILE_NOT_FOUND_OID

        # --- Check permissions

        if not self._profile_modification_allowed(channel_oid, user_oid, target_oid):
            return OperationOutcome.X_INSUFFICIENT_PERMISSION

        # --- Check profile attachable

        attachable_profiles = self.get_attachable_profiles(channel_oid, user_oid)
        if not attachable_profiles:
            return OperationOutcome.X_NO_ATTACHABLE_PROFILES

        if not any(prof.id == profile_oid for prof in attachable_profiles):
            return OperationOutcome.X_UNATTACHABLE

        # --- Attach profile

        return self._conn.user_attach_profile(channel_oid, target_oid, profile_oid)

    @arg_type_ensure
    def detach_profile_name(self, channel_oid: ObjectId, profile_name: str, user_oid: ObjectId,
                            target_oid: Optional[ObjectId] = None) \
            -> OperationOutcome:
        prof = self.get_profile_name(channel_oid, profile_name)
        if not prof:
            return OperationOutcome.X_PROFILE_NOT_FOUND_NAME

        return self.detach_profile(channel_oid, prof.id, user_oid, target_oid)

    def detach_profile(self, channel_oid: ObjectId, profile_oid: ObjectId, user_oid: ObjectId,
                       target_oid: Optional[ObjectId] = None) \
            -> OperationOutcome:
        """
        Detach the profile.

        ``target_oid`` needs to be specified unless to detach the profile from all users.

        .. note::
            Permission check will **NOT** be performed when detaching from all of the users.

        :param channel_oid: channel OID of the profile
        :param profile_oid: OID of the profile
        :param user_oid: user to detach the profile
        :param target_oid: target to be detached the profile
        :return: outcome of the detachment
        """
        # --- Check target

        if not self._conn.is_user_in_channel(channel_oid, user_oid):
            return OperationOutcome.X_EXECUTOR_NOT_IN_CHANNEL

        if target_oid and not self._conn.is_user_in_channel(channel_oid, target_oid):
            return OperationOutcome.X_TARGET_NOT_IN_CHANNEL

        # --- Check profile existence

        if not self.get_profile(profile_oid):
            return OperationOutcome.X_PROFILE_NOT_FOUND_OID

        # --- Check permissions

        if not self._profile_modification_allowed(channel_oid, user_oid, target_oid):
            return OperationOutcome.X_INSUFFICIENT_PERMISSION

        # --- Detach profile

        detach_outcome = self._conn.detach_profile(profile_oid, target_oid)
        if detach_outcome.is_success:
            return OperationOutcome.O_COMPLETED
        else:
            return OperationOutcome.X_DETACH_FAILED

    def delete_profile(self, channel_oid: ObjectId, profile_oid: ObjectId, user_oid: ObjectId) -> OperationOutcome:
        """
        Detach the profile from all users and delete it.

        If the detachment fails, the deletion won't be performed.

        :param channel_oid: channel of the profile
        :param profile_oid: OID of the profile
        :param user_oid: user to perform the profile deletion
        :return: if the deletion succeed
        """
        detach_result = self.detach_profile(channel_oid, profile_oid, user_oid)

        if not detach_result.is_success:
            return detach_result

        return OperationOutcome.O_COMPLETED \
            if self._prof.delete_profile(profile_oid) \
            else OperationOutcome.X_DELETE_FAILED

    def mark_unavailable_async(self, channel_oid: ObjectId, root_oid: ObjectId) -> Thread:
        t = Thread(target=self._conn.mark_unavailable, args=(channel_oid, root_oid))
        t.start()

        return t

    def get_user_profiles(self, channel_oid: ObjectId, root_uid: ObjectId) -> List[ChannelProfileModel]:
        """
        Get the ``list`` of :class:`ChannelProfileModel` of the specified user.

        :param channel_oid: channel OID of the user
        :param root_uid: user OID
        :return: list of the profiles attached on the user
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

    @arg_type_ensure
    def get_channel_profiles(self, channel_oid: ObjectId, prof_name: Optional[str] = None) \
            -> ExtendedCursor[ChannelProfileModel]:
        """
        Get the profiles in a channel.

        If ``prof_name`` is given, the name of the returned profiles must contain (**NOT necessarily** equal to) it.
        If not provided, then all of the profiles of the channel will be returned.

        Returned profiles include the profile which is not being attached to anyone.

        :param channel_oid: channel OID of the profiles
        :param prof_name: name of the profiles
        :return: profiles of the channel
        """
        return self._prof.get_channel_profiles(channel_oid, prof_name)

    @staticmethod
    def get_highest_permission_level(profiles: List[ChannelProfileModel]) -> PermissionLevel:
        current_max = PermissionLevel.lowest()

        for profile in profiles:
            if profile.permission_level > current_max:
                current_max = profile.permission_level

        return current_max

    def get_user_channel_profiles(self, user_oid: ObjectId, *,
                                  inside_only: bool = True, accessbible_only: bool = True) \
            -> List[ChannelProfileListEntry]:
        """
        Get all profiles of a user and group it by channel.

        The sorting order is:

        - Starred (True -> False)

        - Bot accessible (True -> False)

        - Profile Connection OID (Descending)

        :param user_oid: OID of the user to get the profiles
        :param inside_only: only get the channel which the user is inside
        :param accessbible_only: only get the channel which the bot is accessible
        :return: list of the profiles grouped by channel
        """
        if not user_oid:
            return []

        ret = []

        not_found: Dict[ObjectId, Union[ObjectId, List[ObjectId]]] = {}

        channel_oid_list = []
        profile_oid_list = []
        prof_conns = []
        for d in self._conn.get_user_channel_profiles(user_oid, inside_only=inside_only):
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
                not_found[prof_conn.id] = cnl_oid
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

            if not_found_prof_oids:
                # There's some profile not found in the database while ID is registered
                not_found[prof_conn.id] = not_found_prof_oids

            perms = self.get_permissions(prof)
            can_ced_profile = self.can_ced_profile(perms)

            ret.append(
                ChannelProfileListEntry(
                    channel_data=cnl, channel_name=cnl.get_channel_name(user_oid), profiles=prof,
                    starred=prof_conn.starred, default_profile_oid=default_profile_oid,
                    can_ced_profile=can_ced_profile
                ))

        if not_found:
            MailSender.send_email_async(Profile.dangling_content(not_found), subject=Profile.DANGLING_PROF_CONN_DATA)

        return list(sorted(ret, key=lambda item: item.channel_data.bot_accessible, reverse=True))

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelProfileModel]:
        return self._prof.get_profile(profile_oid)

    def get_profile_name(self, channel_oid: ObjectId, name: str) -> Optional[ChannelProfileModel]:
        return self._prof.get_profile_name(channel_oid, name)

    def get_users_exist_channel_dict(self, user_oids: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        """
        Get a :class:`dict` which for each element:

            key is each user listed in ``user_oids`` and

            value is the OIDs of the channel they are in.

        :param user_oids: list of users to be checked
        :return: a `dict` containing the information described above
        """
        return self._conn.get_users_exist_channel_dict(user_oids)

    @classmethod
    def get_permissions(cls, profiles: List[ChannelProfileModel]) -> Set[ProfilePermission]:
        ret = set()

        for prof in profiles:
            for perm_cat, perm_grant in prof.permission.items():
                perm = ProfilePermission.cast(perm_cat, silent_fail=True)
                if perm_grant and perm:
                    ret.add(perm)

            highest_perm_lv = cls.get_highest_permission_level(profiles)
            ret = ret.union(ProfilePermissionDefault.get_overridden_permissions(highest_perm_lv))

        return ret

    def get_user_permissions(self, channel_oid: ObjectId, root_uid: ObjectId) -> Set[ProfilePermission]:
        return self.get_permissions(self.get_user_profiles(channel_oid, root_uid))

    def get_channel_prof_conn(self, channel_oid: Union[ObjectId, List[ObjectId]], *, available_only=False) \
            -> List[ChannelProfileConnectionModel]:
        return self._conn.get_channel_prof_conn(channel_oid, available_only=available_only)

    def get_channel_member_oids(self, channel_oid: Union[ObjectId, List[ObjectId]], *, available_only=False) \
            -> Set[ObjectId]:
        return {mdl.user_oid for mdl in self.get_channel_prof_conn(channel_oid, available_only=available_only)}

    def get_available_connections(self) -> ExtendedCursor[ChannelProfileConnectionModel]:
        return self._conn.get_available_connections()

    def get_attachable_profiles(self, channel_oid: ObjectId, root_uid: ObjectId) -> List[ChannelProfileModel]:
        """
        Get the list of the profiles that the user ``root_uid`` can attach to self or any member
        excluding the default profile.

        The returned result does **NOT** care if the user has sufficient permission or not.

        The returned result will be empty if the user does not have the permission
        to control profile on any type of target.

        :param channel_oid: channel OID of the profiles
        :param root_uid: user OID to get the attachable profiles
        :return: list of the attachable profiles sorted by name
        """
        profiles = self.get_user_profiles(channel_oid, root_uid)
        exist_perm = self.get_permissions(profiles)

        if not self.can_control_profile_member(exist_perm) and not self.can_control_profile_self(exist_perm):
            return []

        highest_perm = self.get_highest_permission_level(profiles)

        # Remove default profile
        channel_data = ChannelManager.get_channel_oid(channel_oid)
        attachables = []
        for prof in self._prof.get_attachable_profiles(channel_oid,
                                                       existing_permissions=exist_perm,
                                                       highest_perm_lv=highest_perm):
            if channel_data and prof.id == channel_data.config.default_profile_oid:
                continue

            attachables.append(prof)

        return list(sorted(attachables, key=lambda x: x.name))

    def get_profile_user_oids(self, profile_oid: ObjectId) -> Set[ObjectId]:
        """
        List of user OIDs who have the profile of ``profile_oid``.

        :param profile_oid: OID of the profile to be checked
        :return: list of user OIDs
        """
        return self._conn.get_profile_user_oids(profile_oid)

    def get_profiles_user_oids(self, profile_oid: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        """
        Get a ``dict`` which
            key is the profile OID provided in ``profile_oid``
            value is the set of user OIDs who have the corresonding profile

        :param profile_oid: OID of the profile to be processed
        :return: a `dict` containing who have the corresopnding profile
        """
        return self._conn.get_profiles_user_oids(profile_oid)

    def is_name_available(self, channel_oid: ObjectId, name: str):
        return self._prof.is_name_available(channel_oid, name)

    @staticmethod
    def can_ced_profile(permissions: Set[ProfilePermission]):
        """CED Stands for Create / Edit / Delete."""
        return ProfilePermission.PRF_CED in permissions

    @staticmethod
    def can_control_profile_member(permissions: Set[ProfilePermission]):
        return ProfilePermission.PRF_CONTROL_MEMBER in permissions

    @staticmethod
    def can_control_profile_self(permissions: Set[ProfilePermission]):
        return ProfilePermission.PRF_CONTROL_SELF in permissions


UserProfileManager = _UserProfileManager()
ProfileDataManager = _ProfileDataManager()
PermissionPromotionRecordHolder = _PermissionPromotionRecordHolder()
ProfileManager = _ProfileManager()
