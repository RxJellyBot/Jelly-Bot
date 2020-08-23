"""
Profile-related data controllers.

:class:`ProfileManager` is the main class to control profiles.

    - Any controls besides tests and access to permission promotion record should use
      this class to manipulate the profile data.
"""
from threading import Thread
from typing import Optional, List, Dict, Set, Union, Iterable

from bson import ObjectId

from env_var import is_testing
from extutils.boolext import to_bool
from extutils.color import ColorFactory
from extutils.checker import arg_type_ensure
from extutils.emailutils import MailSender
from flags import ProfilePermission, ProfilePermissionDefault, PermissionLevel
from mixin import ClearableMixin
from models import ChannelProfileListEntry, ChannelProfileModel, ChannelProfileConnectionModel, ChannelModel
from models.exceptions import ModelConstructionError, RequiredKeyNotFilledError, InvalidModelFieldError
from mongodb.factory import ChannelManager
from mongodb.factory.results import (
    WriteOutcome, OperationOutcome, UpdateOutcome,
    CreateProfileResult, RegisterProfileResult, ArgumentParseResult
)
from mongodb.utils import ExtendedCursor
from strres.mongodb import Profile

from .prof_base import UserProfileManager, ProfileDataManager, PermissionPromotionRecordHolder

__all__ = ("ProfileManager",)


class _ProfileManager(ClearableMixin):
    # pylint: disable=too-many-public-methods

    @staticmethod
    def _create_kwargs_channel_oid(ret_kwargs, profile_fkwargs) -> Optional[ArgumentParseResult]:
        fk_coid = ChannelProfileModel.json_key_to_field(ChannelProfileModel.ChannelOid.key)
        if fk_coid not in profile_fkwargs:
            return ArgumentParseResult(OperationOutcome.X_MISSING_CHANNEL_OID)

        try:
            coid = ObjectId(profile_fkwargs[fk_coid])
        except Exception as ex:
            return ArgumentParseResult(OperationOutcome.X_INVALID_CHANNEL_OID, ex)

        ret_kwargs[fk_coid] = coid
        return None

    @staticmethod
    def _create_kwargs_perm_lv(ret_kwargs, profile_fkwargs) -> Optional[ArgumentParseResult]:
        fk_perm_lv = ChannelProfileModel.json_key_to_field(ChannelProfileModel.PermissionLevel.key)
        if fk_perm_lv not in profile_fkwargs:
            return None

        try:
            perm_lv = PermissionLevel.cast(profile_fkwargs[fk_perm_lv])
        except (TypeError, ValueError) as ex:
            return ArgumentParseResult(OperationOutcome.X_INVALID_PERM_LV, ex)

        ret_kwargs[fk_perm_lv] = perm_lv
        return None

    @staticmethod
    def _create_kwargs_permission(ret_kwargs, profile_fkwargs):
        fk_perm = ChannelProfileModel.json_key_to_field(ChannelProfileModel.Permission.key)
        fk_perm_initial = f"{fk_perm}."
        perm_dict = {}
        keys_to_remove = set()

        # Fill turned-on permissions
        for fk in profile_fkwargs:
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

    @staticmethod
    def _create_kwargs_color(ret_kwargs, profile_fkwargs):
        fk_color = ChannelProfileModel.json_key_to_field(ChannelProfileModel.Color.key)
        if fk_color not in profile_fkwargs:
            return None

        try:
            color = ColorFactory.from_hex(profile_fkwargs[fk_color])
        except ValueError as ex:
            return ArgumentParseResult(OperationOutcome.X_INVALID_COLOR, ex)

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
        self._conn = UserProfileManager
        self._prof = ProfileDataManager
        self._promo = PermissionPromotionRecordHolder

    def clear(self):
        self._conn.clear()
        self._prof.clear()
        self._promo.clear()

    # region Create

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

        # Controlling self
        if target_oid and user_oid == target_oid:
            return ProfilePermission.PRF_CONTROL_SELF in permissions

        return ProfilePermission.PRF_CONTROL_MEMBER in permissions

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
        """
        Register a user with the default profile of that channel.

        :param channel_oid: channel of the user
        :param root_uid: OID of the user
        :return: result of the profile registration
        """
        attach_outcome = OperationOutcome.X_NOT_EXECUTED
        prof_result = self._prof.get_default_profile(channel_oid)

        if prof_result.success:
            attach_outcome = self._conn.user_attach_profile(channel_oid, root_uid, prof_result.model.id)

        return RegisterProfileResult(prof_result.outcome, prof_result.exception, prof_result.model, attach_outcome)

    def register_new_default_async(self, channel_oid: ObjectId, root_uid: ObjectId):
        """
        Same functionality as ``register_new_default`` but execute the method asynchronously.

        The method will be executed synchronously if ``TEST`` in environment variable is true.

        :param channel_oid: channel of the user
        :param root_uid: OID of the user
        """
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

    # endregion

    # region Update / Modify

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
        """
        Detach the profile which name is ``profile_name`` from ``target_oid`` in ``channel_oid`` as ``user_oid``.

        If ``target_oid`` is ``None``, the method will consider that the executor wants to detach the profile from
        themselves.

        :param channel_oid: channel of the profile to be detached
        :param profile_name: name of the profile to be detached
        :param user_oid: OID of the action executor
        :param target_oid: target to be detached the profile
        :return: outcome of the profile detachment
        """
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
        if not detach_outcome.is_success:
            return OperationOutcome.X_DETACH_FAILED

        return OperationOutcome.O_COMPLETED

    def mark_unavailable_async(self, channel_oid: ObjectId, root_oid: ObjectId) -> Thread:
        """
        Mark the user ``root_oid`` in the channel ``channel_oid`` unavailable asynchronously.

        This method returns the :class:`Thread` of marking the user unavailable which is started already.

        :param channel_oid: channel of the user to be marked
        :param root_oid: user to be marked unavailable
        :return: started thread which marks the user unavailable
        """
        thread = Thread(target=self._conn.mark_unavailable, args=(channel_oid, root_oid))
        thread.start()

        return thread

    # endregion

    # region Delete

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

    # endregion

    # region Get information related to profile

    def get_user_profiles(self, channel_oid: ObjectId, root_uid: ObjectId) -> List[ChannelProfileModel]:
        """
        Get the ``list`` of :class:`ChannelProfileModel` of the specified user.

        :param channel_oid: channel OID of the user
        :param root_uid: user OID
        :return: list of the profiles attached on the user
        """
        conn = self._conn.get_user_profile_conn(channel_oid, root_uid)

        if not conn:
            return []

        ret = []
        for poid in conn.profile_oids:
            prof = self._prof.get_profile(poid)
            if prof:
                ret.append(prof)

        return ret

    def _get_user_channel_profiles_prep_data(self, user_oid: ObjectId, inside_only: bool):
        channel_oid_list = []
        profile_oid_list = []
        prof_conns = []
        for prof_conn in self._conn.get_user_channel_prof_conns(user_oid, inside_only=inside_only):
            channel_oid_list.append(prof_conn.channel_oid)
            profile_oid_list.extend(prof_conn.profile_oids)
            prof_conns.append(prof_conn)

        channel_dict = ChannelManager.get_channel_dict(channel_oid_list, accessbible_only=False)
        profile_dict = self._prof.get_profile_dict(profile_oid_list)

        return channel_dict, profile_dict, prof_conns

    @classmethod
    def _get_user_channel_profiles_get_channel_model(cls, prof_conn: ChannelProfileConnectionModel,
                                                     channel_dict: Dict[ObjectId, ChannelModel],
                                                     not_found_dict: Dict[ObjectId, Union[ObjectId, List[ObjectId]]],
                                                     accessbible_only: bool):
        cnl_oid = prof_conn.channel_oid
        cnl = channel_dict.get(cnl_oid)

        if not cnl:
            not_found_dict[prof_conn.id] = cnl_oid
            return None

        if accessbible_only and not cnl.bot_accessible:
            return None

        return cnl

    @classmethod
    def _get_user_channel_profiles_get_profile_models(cls, prof_conn: ChannelProfileConnectionModel,
                                                      profile_dict: Dict[ObjectId, ChannelProfileModel],
                                                      not_found_dict: Dict[ObjectId, Union[ObjectId, List[ObjectId]]]):
        profs = []
        not_found_prof_oids = []

        for prof_oid in prof_conn.profile_oids:
            prof_mdl = profile_dict.get(prof_oid)
            if prof_mdl:
                profs.append(prof_mdl)
            else:
                not_found_prof_oids.append(prof_oid)

        if not_found_prof_oids:
            # There's some profile not found in the database while ID is registered
            not_found_dict[prof_conn.id] = not_found_prof_oids

        return profs

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

        channel_dict, profile_dict, prof_conns = self._get_user_channel_profiles_prep_data(user_oid, inside_only)

        for prof_conn in prof_conns:
            # Get Channel Model
            cnl = self._get_user_channel_profiles_get_channel_model(prof_conn, channel_dict,
                                                                    not_found, accessbible_only)
            if not cnl:
                continue

            default_profile_oid = cnl.config.default_profile_oid

            # Get Profile Model
            profs = self._get_user_channel_profiles_get_profile_models(prof_conn, profile_dict, not_found)

            ret.append(
                ChannelProfileListEntry(
                    channel_data=cnl, channel_name=cnl.get_channel_name(user_oid), profiles=profs,
                    starred=prof_conn.starred, default_profile_oid=default_profile_oid,
                    can_ced_profile=self.can_ced_profile(self.get_permissions(profs))
                ))

        if not_found:
            MailSender.send_email_async(Profile.dangling_content(not_found), subject=Profile.DANGLING_PROF_CONN_DATA)

        return list(sorted(ret, key=lambda item: item.channel_data.bot_accessible, reverse=True))

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

    def get_profile(self, profile_oid: ObjectId) -> Optional[ChannelProfileModel]:
        """
        Get the profile of OID ``profile_oid``

        :param profile_oid: OID of the profile to get
        :return: `ChannelProfileModel` if found, `None` otherwise
        """
        return self._prof.get_profile(profile_oid)

    def get_profile_name(self, channel_oid: ObjectId, name: str) -> Optional[ChannelProfileModel]:
        """
        Get a profile in ``channel_oid`` which name is exactly ``name``.

        ``name`` will be stripped before the query.

        :param channel_oid: channel of the profile
        :param name: exact name of the profile to get
        :return: `ChannelProfileModel` if found, `None` otherwise
        """
        return self._prof.get_profile_name(channel_oid, name)

    def get_profile_user_oids(self, profile_oid: ObjectId) -> Set[ObjectId]:
        """
        List of user OIDs who have the profile of ``profile_oid``.

        :param profile_oid: OID of the profile to be checked
        :return: list of user OIDs
        """
        return self._conn.get_profile_user_oids(profile_oid)

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

    # endregion

    # region Get information from profiles/permissions

    @staticmethod
    def get_highest_permission_level(profiles: Iterable[ChannelProfileModel]) -> PermissionLevel:
        """
        Get the highest permission level of ``profiles``.

        This method only check the permission level of the profiles. It ignores the permission field.

        :param profiles: profiles to get the highest permission level
        :return: highest permission level among the profiles
        """
        return max({prof.permission_level for prof in profiles}, default=PermissionLevel.lowest())

    @classmethod
    def get_permissions(cls, profiles: List[ChannelProfileModel]) -> Set[ProfilePermission]:
        """
        Get a set of allowed permissions in ``profiles``.

        :param profiles: profiles to get the allowed permissions
        :return: a set of allowed permissions
        """
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
        """
        Get the permissions of the user ``root_uid`` in channel ``channel_oid``.

        :param channel_oid: channel of the user to get the permissions
        :param root_uid: user to get the permissions
        :return: a set of permissions that the user has
        """
        return self.get_permissions(self.get_user_profiles(channel_oid, root_uid))

    def get_channel_prof_conn(self, channel_oid: Union[ObjectId, List[ObjectId]], *, available_only=False) \
            -> List[ChannelProfileConnectionModel]:
        """
        Get all profile connections in the selected channel(s).

        ``channel_oid`` can be either a single :class:`ObjectId` or a :class:`list` of :class:`ObjectId`.

        :param channel_oid: channel to get the profile connections
        :param available_only: if to only get the connections attached to the available user
        :return: list of `ChannelProfileConnectionModel`
        """
        return self._conn.get_channel_prof_conn(channel_oid, available_only=available_only)

    def get_channel_member_oids(self, channel_oid: Union[ObjectId, List[ObjectId]], *, available_only=False) \
            -> Set[ObjectId]:
        """
        Get a set of user OIDs that are the member of ``channel_oid``.

        ``channel_oid`` can be either a single channel (one OID) or a list of channels (list of OIDs).

        If ``channel_oid`` is a list, then each returned UID means that they are a member of one of the channels in
        ``channel_oid``.

        :param channel_oid: channel(s) to check the member
        :param available_only: if to only return the available members
        :return: set of user OIDs that are the member of the given channel(s)
        """
        return {mdl.user_oid for mdl in self.get_channel_prof_conn(channel_oid, available_only=available_only)}

    def get_available_connections(self) -> ExtendedCursor[ChannelProfileConnectionModel]:
        """
        Get the cursor which yields only the connections to the available users.

        :return: cursor of the connections to the available users
        """
        return self._conn.get_available_connections()

    # endregion

    # region Get data for batch process

    def get_users_exist_channel_dict(self, user_oids: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        """
        Get a :class:`dict` which for each element:

            key is each user listed in ``user_oids`` and

            value is the OIDs of the channel they are in.

        :param user_oids: list of users to be checked
        :return: a `dict` containing the information described above
        """
        return self._conn.get_users_exist_channel_dict(user_oids)

    def get_user_permission_lv_dict(self, channel_oid: ObjectId) -> Dict[ObjectId, PermissionLevel]:
        """
        Get a ``dict`` which key is the user OID and value is their highest permission level.

        :param channel_oid: OID of the channel to check the highest permission level of the members
        :return: a `dict` containing the user OIDs pointing to their highest permission level
        """
        user_prof_dict = self._conn.get_user_profile_dict(channel_oid)
        prof_oids = set()
        for prof_oids_user in user_prof_dict.values():
            prof_oids |= prof_oids_user

        prof_dict = self._prof.get_profile_dict(list(prof_oids))

        ret = {}

        for uid, prof_oids_user in user_prof_dict.items():
            ret[uid] = self.get_highest_permission_level({prof_dict[prof_oid] for prof_oid in prof_oids_user})

        return ret

    def get_profiles_user_oids(self, profile_oid: List[ObjectId]) -> Dict[ObjectId, Set[ObjectId]]:
        """
        Get a :class:`dict` where key is the profile OID and the value is a set of user OIDs who have th profile.

        :param profile_oid: OID of the profile to be processed
        :return: a `dict` containing who have the corresopnding profile
        """
        return self._conn.get_profiles_user_oids(profile_oid)

    # endregion

    # region Check info from profiles/permissions

    def is_name_available(self, channel_oid: ObjectId, name: str):
        """
        Check if the profile name ``name`` is available in the channel ``channel_oid``.

        ``name`` will be stipped before the check.

        :param channel_oid: channel for the profile to check the availablility
        :param name: name of the profile to be checked
        :return: if the profile name is available
        """
        return self._prof.is_name_available(channel_oid, name)

    @staticmethod
    def can_ced_profile(permissions: Set[ProfilePermission]) -> bool:
        """
        Check if the user can Control/Edit/Delete the profile by checking the given ``permissions``.

        :param permissions: permissions to be checked
        :return: if `ProfilePermission.PRF_CED` is in `permissions`
        """
        return ProfilePermission.PRF_CED in permissions

    @staticmethod
    def can_control_profile_member(permissions: Set[ProfilePermission]):
        """
        Check if the user can control profiles on channel members by checking the given ``permissions``.

        :param permissions: permissions to be checked
        :return: if `ProfilePermission.PRF_CONTROL_MEMBER` is in `permissions`
        """
        return ProfilePermission.PRF_CONTROL_MEMBER in permissions

    @staticmethod
    def can_control_profile_self(permissions: Set[ProfilePermission]):
        """
        Check if the user can control profiles on themselves by checking the given ``permissions``.

        :param permissions: permissions to be checked
        :return: if `ProfilePermission.PRF_CONTROL_SELF` is in `permissions`
        """
        return ProfilePermission.PRF_CONTROL_SELF in permissions

    # endregion


ProfileManager = _ProfileManager()
