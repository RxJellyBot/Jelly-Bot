"""Data managers for the channel-related connections."""
from typing import Optional, Dict, List

import pymongo
from bson import ObjectId
from pymongo import ReturnDocument

from extutils.checker import arg_type_ensure
from flags import Platform
from models import ChannelModel, ChannelConfigModel, ChannelCollectionModel, OID_KEY
from mongodb.utils import ExtendedCursor
from mongodb.factory.results import (
    WriteOutcome, GetOutcome, OperationOutcome, UpdateOutcome,
    ChannelRegistrationResult, ChannelGetResult, ChannelChangeNameResult, ChannelCollectionRegistrationResult
)

from ._base import BaseCollection

__all__ = ("ChannelManager", "ChannelCollectionManager",)

DB_NAME = "channel"


class _ChannelManager(BaseCollection):
    """Class to manage the channel data."""

    database_name = DB_NAME
    collection_name = "dict"
    model_class = ChannelModel

    def build_indexes(self):
        self.create_index(
            [(ChannelModel.Platform.key, 1), (ChannelModel.Token.key, 1)], name="Channel Identity", unique=True)

    @arg_type_ensure
    def ensure_register(self, platform: Platform, token: str, *, default_name: str = None) \
            -> ChannelRegistrationResult:
        """
        Register the channel if not yet registered.

        Returning result contains the existing or registered :class:`ChannelModel`.

        :param platform: platform of the channel
        :param token: token of the channel
        :param default_name: default name to be used if channel not yet registered
        :return: channel registration result
        """
        mdl = self.get_channel_token(platform, token)

        if mdl:
            return ChannelRegistrationResult(WriteOutcome.O_DATA_EXISTS, model=mdl)

        # Inline import to avoid cyclic import
        from mongodb.factory import ProfileManager  # pylint: disable=import-outside-toplevel

        channel_oid = ObjectId()
        create_result = ProfileManager.create_default_profile(
            channel_oid, set_to_channel=False, check_channel=False)

        if not create_result.success:
            return ChannelRegistrationResult(WriteOutcome.X_CNL_DEFAULT_CREATE_FAILED)

        config = ChannelConfigModel.generate_default(
            DefaultName=default_name, DefaultProfileOid=create_result.model.id)

        mdl, outcome, ex = self.insert_one_data(Id=channel_oid, Platform=platform, Token=token, Config=config)

        return ChannelRegistrationResult(outcome, ex, mdl)

    @arg_type_ensure
    def deregister(self, platform: Platform, token: str) -> UpdateOutcome:
        """
        Mark the channel as inaccessible.

        :param platform: platform of the channel
        :param token: token of the channel
        :return: outcome of the marking
        """
        return self.mark_accessibility(platform, token, False)

    @arg_type_ensure
    def mark_accessibility(self, platform: Platform, token: str, accessibility: bool) -> UpdateOutcome:
        """
        To mark the accessibility of a channel as ``accessibility``.

        :param platform: platform of the channel
        :param token: token of the channel
        :param accessibility: new accessibility of the channel
        :return: outcome of the marking
        """
        result = self.update_many_outcome(
            {ChannelModel.Platform.key: platform, ChannelModel.Token.key: token},
            {"$set": {ChannelModel.BotAccessible.key: accessibility}}
        )
        if result == UpdateOutcome.X_NOT_FOUND:
            return UpdateOutcome.X_CHANNEL_NOT_FOUND

        return result

    @arg_type_ensure
    def update_channel_default_name(self, platform: Platform, token: str, default_name: str) -> UpdateOutcome:
        """
        Update the default name of a channel.

        :param platform: platform of the channel to be updated
        :param token: token of the channel to be updated
        :param default_name: new default name for the channel
        :return: outcome of the update
        """
        return self.update_many_outcome(
            {ChannelModel.Platform.key: platform, ChannelModel.Token.key: token},
            {"$set": {f"{ChannelModel.Config.key}.{ChannelConfigModel.DefaultName.key}": default_name}}
        )

    @arg_type_ensure
    def update_channel_nickname(self, channel_oid: ObjectId, root_oid: ObjectId, new_name: str) \
            -> ChannelChangeNameResult:
        """
        Update the channel name for the user.

        If ``new_name`` is falsy, then the user-specific name will be removed.

        :param channel_oid: channel of the user to update the nickname
        :param root_oid: user to update the nickname
        :param new_name: new channel nick name
        :return: result of the channel nickname change
        """
        ex = None
        if new_name:
            ret = self.find_one_and_update(
                {ChannelModel.Id.key: channel_oid},
                {"$set": {f"{ChannelModel.Name.key}.{root_oid}": new_name}},
                return_document=ReturnDocument.AFTER)
        else:
            ret = self.find_one_and_update(
                {ChannelModel.Id.key: channel_oid},
                {"$unset": {f"{ChannelModel.Name.key}.{root_oid}": ""}},
                return_document=ReturnDocument.AFTER)

        try:
            if ret:
                outcome = OperationOutcome.O_COMPLETED
                ret = ChannelModel.cast_model(ret)
            else:
                outcome = OperationOutcome.X_CHANNEL_NOT_FOUND
        except Exception as e:
            outcome = OperationOutcome.X_ERROR
            ex = e

        return ChannelChangeNameResult(outcome, ex, ret)

    @arg_type_ensure
    def get_channel_token(self, platform: Platform, token: str, *,
                          auto_register: bool = False, default_name: str = None) \
            -> Optional[ChannelModel]:
        """
        Get the :class:`ChannelModel` by channel token.

        :param platform: platform of the channel to get
        :param token: token of the channel to get
        :param auto_register: automatically register the channel if not found
        :param default_name: default name of the channel to use for registration if wanted
        :return: `ChannelModel` matching the given condition. `None` otherwise
        """
        ret = self.find_one_casted({ChannelModel.Token.key: token, ChannelModel.Platform.key: platform})

        if not ret and auto_register:
            reg_result = self.ensure_register(platform, token, default_name=default_name)
            if reg_result.success:
                ret = reg_result.model
            else:
                raise ValueError(
                    f"Channel registration failed in `ChannelManager.get_channel_token`. "
                    f"Platform: {platform} / Token: {token}")

        return ret

    @arg_type_ensure
    def get_channel_oid(self, channel_oid: ObjectId, *, hide_private: bool = False) -> Optional[ChannelModel]:
        """
        Get the :class:`ChannelModel` by its OID.

        Returns ``None`` if not found.

        :param channel_oid: OID of the channel to get
        :param hide_private: to hide private channel
        :return: a `ChannelModel` which ID is `channel_oid`
        """
        filter_ = {ChannelModel.Id.key: channel_oid}

        if hide_private:
            filter_[f"{ChannelModel.Config.key}.{ChannelConfigModel.InfoPrivate.key}"] = False

        return self.find_one_casted(filter_)

    def get_channel_dict(self, channel_oid_list: List[ObjectId], *, accessbible_only: bool = False) \
            -> Dict[ObjectId, ChannelModel]:
        """
        Get a :class:`dict` which key is the channel OID and value is its corresponding ``ChannelModel``.

        The

        :param channel_oid_list: list of OIDs of the channel to get
        :param accessbible_only: to get accessible channels only
        :return: a `dict` which key is channel OID and value is its corresponding `ChannelModel`
        """
        filter_ = {OID_KEY: {"$in": channel_oid_list}}

        if accessbible_only:
            filter_[ChannelModel.BotAccessible.key] = True

        return {model.id: model for model in self.find_cursor_with_count(filter_)}

    @arg_type_ensure
    def get_channel_default_name(self, default_name: str, *, hide_private: bool = True) \
            -> ExtendedCursor[ChannelModel]:
        """
        Get a list of channels which default name or token contains a part or all of ``default_name``.

        Returned result will be sorted by channel OID (DESC).

        :param default_name: default name or part of the token of a channel
        :param hide_private: hide private channel from this search
        :return: a cursor yielding the channels that match the conditions
        """
        filter_ = {
            "$or": [
                {
                    f"{ChannelModel.Token.key}": {"$regex": default_name, "$options": "i"}
                },
                {
                    f"{ChannelModel.Config.key}.{ChannelConfigModel.DefaultName.key}":
                        {"$regex": default_name, "$options": "i"}
                }
            ]
        }

        if hide_private:
            filter_[f"{ChannelModel.Config.key}.{ChannelConfigModel.InfoPrivate.key}"] = False

        return self.find_cursor_with_count(filter_, sort=[(ChannelModel.Id.key, pymongo.DESCENDING)])

    def get_channel_packed(self, platform: Platform, token: str) -> ChannelGetResult:
        """
        Get the channel by its token and pack the result.

        :param platform: platform of the channel to get
        :param token: token of the channel to get
        :return: result of getting the channel
        """
        model = self.get_channel_token(platform, token)

        if model is not None:
            outcome = GetOutcome.O_CACHE_DB
        else:
            outcome = GetOutcome.X_CHANNEL_NOT_FOUND

        return ChannelGetResult(outcome, model=model)

    def set_config(self, channel_oid: ObjectId, json_key: str, config_value) -> UpdateOutcome:
        """
        Set/update the channel config.

        The config model is :class:`ChannelConfigModel`. ``json_key`` correspondance can be found in this model.

        :param channel_oid: OID of the channel to be updated
        :param json_key: json key of the config to be updated
        :param config_value: new config value
        :return: outcome of the update
        """
        if json_key not in ChannelConfigModel.model_json_keys():
            return UpdateOutcome.X_CONFIG_NOT_EXISTS

        fk = ChannelConfigModel.json_key_to_field(json_key)
        if not getattr(ChannelConfigModel, fk).is_type_matched(config_value):
            return UpdateOutcome.X_CONFIG_TYPE_MISMATCH

        if not getattr(ChannelConfigModel, fk).is_value_valid(config_value):
            return UpdateOutcome.X_CONFIG_VALUE_INVALID

        result = self.update_one_outcome(
            {ChannelModel.Id.key: channel_oid},
            {"$set": {f"{ChannelModel.Config.key}.{json_key}": config_value}})

        if result == UpdateOutcome.X_NOT_FOUND:
            return UpdateOutcome.X_CHANNEL_NOT_FOUND

        return result


class _ChannelCollectionManager(BaseCollection):
    """
    Channel to manage the channel collection data.

    Currently, LINE does not have the concept of channel collection.
    However, in Discord, this concept is called a server (guild in ``discord.py``).
    """

    # TEST: ChannelCollectionManager

    database_name = DB_NAME
    collection_name = "collection"
    model_class = ChannelCollectionModel

    def build_indexes(self):
        self.create_index(
            [(ChannelCollectionModel.Platform.key, 1), (ChannelCollectionModel.Token.key, 1)],
            name="Channel Collection Identity", unique=True)
        self.create_index(ChannelCollectionModel.ChildChannelOids.key, name="Child Channel Index")

    @arg_type_ensure
    def ensure_register(self, platform: Platform, token: str,
                        child_channel_oid: ObjectId, default_name: Optional[str] = None) \
            -> ChannelCollectionRegistrationResult:
        """
        Ensure that the channel collection is registered.

        ``default_name`` will be used if the channel collection is not found.

        If ``default_name`` is ``None``, it will be in the format of **<TOKEN> (<PLATFORM>)**.

        If the channel collection has not been registered,
        register it with ``platform``, ``token`` and ``default_name``.

        If the channel collection has been registered, but not the ``child_channel_oid``,
        append it to the channel collection.

        :param platform: platform of the channel collection
        :param token: token of the channel collection
        :param child_channel_oid: OID of the current channel which belongs to the given channel connection
        :param default_name: default name of the channel collection to use if not registered
        :return: channel collection registration result
        """
        if not default_name:
            default_name = f"{token} ({platform.key})"

        entry, outcome, ex = self.insert_one_data(
            DefaultName=default_name, Platform=platform, Token=token, ChildChannelOids=[child_channel_oid])

        if outcome.data_found:
            entry = self.get_chcoll(platform, token)
            self.append_child_channel(entry.id, child_channel_oid)

        return ChannelCollectionRegistrationResult(outcome, ex, entry)

    @arg_type_ensure
    def get_chcoll(self, platform: Platform, token: str) -> Optional[ChannelCollectionModel]:
        """
        Get the channel collection by its ``platform`` and ``token``.

        :param platform: platform of the channel collection to get
        :param token: token of the channel collection to get
        :return: `ChannelCollectionModel` if found, `None` otherwise
        """
        return self.find_one_casted(
            {ChannelCollectionModel.Token.key: token, ChannelCollectionModel.Platform.key: platform}
        )

    @arg_type_ensure
    def get_chcoll_oid(self, chcoll_oid: ObjectId) -> Optional[ChannelCollectionModel]:
        """
        Get the channel collection by its ``chcoll_oid``.

        :param chcoll_oid: OID of the channel collection to get
        :return: `ChannelCollectionModel` if found, `None` otherwise
        """
        return self.find_one_casted(
            {ChannelCollectionModel.Id.key: chcoll_oid}
        )

    @arg_type_ensure
    def get_chcoll_child_channel(self, child_channel_oid: ObjectId):
        """
        Get the channel collection by one of its ``child_channel_oid``.

        :param child_channel_oid: one of the child channel OIDs of the channel collection to get
        :return: `ChannelCollectionModel` if found, `None` otherwise
        """
        return self.find_one_casted(
            {ChannelCollectionModel.ChildChannelOids.key: child_channel_oid}
        )

    @arg_type_ensure
    def append_child_channel(self, parent_oid: ObjectId, channel_oid: ObjectId) -> UpdateOutcome:
        """
        Append ``channel_oid`` to the channel collection ``parent_oid``.

        :param parent_oid: OID of the channel collection to attach
        :param channel_oid: OID of the channel to be attached to the channel collection
        :return: outcome of the attachment
        """
        return self.update_many_outcome(
            {ChannelCollectionModel.Id.key: parent_oid},
            {"$addToSet": {ChannelCollectionModel.ChildChannelOids.key: channel_oid}})

    @arg_type_ensure
    def update_default_name(self, platform: Platform, token: str, new_default_name: str) -> UpdateOutcome:
        """
        Update the default name of the channel collection.

        :param platform: platform of the channel collection to update
        :param token: token of the channel collection to update
        :param new_default_name: new default name of the channel collection
        :return: outcome of the update
        """
        return self.update_many_outcome(
            {ChannelCollectionModel.Token.key: token, ChannelCollectionModel.Platform.key: platform},
            {"$set": {ChannelCollectionModel.DefaultName.key: new_default_name}})


ChannelManager = _ChannelManager()
ChannelCollectionManager = _ChannelCollectionManager()
