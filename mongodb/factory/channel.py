from typing import Optional, Dict, List

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

__all__ = ["ChannelManager", "ChannelCollectionManager"]

DB_NAME = "channel"


class _ChannelManager(BaseCollection):
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

        Return the existing or registered :class:`ChannelModel`.
        """
        mdl = self.get_channel_token(platform, token)

        if not mdl:
            # Inline import because it will create a loop if imported outside
            from mongodb.factory import ProfileManager

            channel_oid = ObjectId()
            create_result = ProfileManager.create_default_profile(channel_oid, set_to_channel=False)

            if not create_result.success:
                return ChannelRegistrationResult(WriteOutcome.X_CNL_DEFAULT_CREATE_FAILED)

            config = ChannelConfigModel.generate_default(
                DefaultName=default_name, DefaultProfileOid=create_result.model.id)

            mdl, outcome, ex = self.insert_one_data(Platform=platform, Token=token, Config=config)

            return ChannelRegistrationResult(outcome, ex, mdl)

        return ChannelRegistrationResult(WriteOutcome.O_DATA_EXISTS, model=mdl)

    @arg_type_ensure
    def deregister(self, platform: Platform, token: str) -> UpdateOutcome:
        return self.mark_accessibility(platform, token, False)

    @arg_type_ensure
    def mark_accessibility(self, platform: Platform, token: str, accessibility: bool) -> UpdateOutcome:
        result = self.update_many_outcome(
            {ChannelModel.Platform.key: platform, ChannelModel.Token.key: token},
            {"$set": {ChannelModel.BotAccessible.key: accessibility}}
        )
        if result == UpdateOutcome.X_NOT_FOUND:
            return UpdateOutcome.X_CHANNEL_NOT_FOUND
        else:
            return result

    @arg_type_ensure
    def update_channel_default_name(self, platform: Platform, token: str, default_name: str) -> UpdateOutcome:
        return self.update_many_outcome(
            {ChannelModel.Platform.key: platform, ChannelModel.Token.key: token},
            {"$set": {f"{ChannelModel.Config.key}.{ChannelConfigModel.DefaultName.key}": default_name}}
        )

    @arg_type_ensure
    def update_channel_nickname(self, channel_oid: ObjectId, root_oid: ObjectId, new_name: str) \
            -> ChannelChangeNameResult:
        """
        Update the channel name for the user. If ``new_name`` is falsy, then the user-specific name will be removed.
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
        ret = self.find_one_casted(
            {ChannelModel.Token.key: token, ChannelModel.Platform.key: platform}, parse_cls=ChannelModel)

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
        filter_ = {ChannelModel.Id.key: channel_oid}

        if hide_private:
            filter_[f"{ChannelModel.Config.key}.{ChannelConfigModel.InfoPrivate.key}"] = False

        return self.find_one_casted(filter_, parse_cls=ChannelModel)

    def get_channel_dict(self, channel_oid_list: List[ObjectId], *, accessbible_only: bool = False) \
            -> Dict[ObjectId, ChannelModel]:
        filter_ = {OID_KEY: {"$in": channel_oid_list}}

        if accessbible_only:
            filter_[ChannelModel.BotAccessible.key] = True

        return {model.id: model for model
                in self.find_cursor_with_count(filter_, parse_cls=ChannelModel)}

    @arg_type_ensure
    def get_channel_default_name(self, default_name: str, *, hide_private: bool = True) \
            -> ExtendedCursor[ChannelModel]:
        filter_ = \
            {"$or": [
                {
                    f"{ChannelModel.Token.key}": {"$regex": default_name, "$options": "i"}
                },
                {
                    f"{ChannelModel.Config.key}.{ChannelConfigModel.DefaultName.key}":
                        {"$regex": default_name, "$options": "i"}
                }
            ]}

        if hide_private:
            filter_[f"{ChannelModel.Config.key}.{ChannelConfigModel.InfoPrivate.key}"] = False

        return self.find_cursor_with_count(filter_, parse_cls=ChannelModel)

    def get_channel_packed(self, platform: Platform, token: str) -> ChannelGetResult:
        model = self.get_channel_token(platform, token)

        if model is not None:
            outcome = GetOutcome.O_CACHE_DB
        else:
            outcome = GetOutcome.X_CHANNEL_NOT_FOUND

        return ChannelGetResult(outcome, model=model)

    def set_config(self, channel_oid: ObjectId, json_key, config_value) -> UpdateOutcome:
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
        else:
            return result


class _ChannelCollectionManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "collection"
    model_class = ChannelCollectionModel

    def build_indexes(self):
        self.create_index(
            [(ChannelCollectionModel.Platform.key, 1), (ChannelCollectionModel.Token.key, 1)],
            name="Channel Collection Identity", unique=True)
        self.create_index(ChannelCollectionModel.ChildChannelOids.key, name="Child Channel Index")

    @arg_type_ensure
    def ensure_register(
            self, platform: Platform, token: str, child_channel_oid: ObjectId, default_name: Optional[str] = None) \
            -> ChannelCollectionRegistrationResult:
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
        return self.find_one_casted(
            {ChannelCollectionModel.Token.key: token, ChannelCollectionModel.Platform.key: platform},
            parse_cls=ChannelCollectionModel)

    @arg_type_ensure
    def get_chcoll_oid(self, chcoll_oid: ObjectId) -> Optional[ChannelCollectionModel]:
        return self.find_one_casted(
            {ChannelCollectionModel.Id.key: chcoll_oid},
            parse_cls=ChannelCollectionModel
        )

    @arg_type_ensure
    def get_chcoll_child_channel(self, child_channel_oid: ObjectId):
        return self.find_one_casted(
            {ChannelCollectionModel.ChildChannelOids.key: child_channel_oid},
            parse_cls=ChannelCollectionModel
        )

    @arg_type_ensure
    def append_child_channel(self, parent_oid: ObjectId, channel_oid: ObjectId) -> UpdateOutcome:
        return self.update_many_outcome(
            {ChannelCollectionModel.Id.key: parent_oid},
            {"$addToSet": {ChannelCollectionModel.ChildChannelOids.key: channel_oid}})

    @arg_type_ensure
    def update_default_name(self, platform: Platform, token: str, new_default_name: str) -> UpdateOutcome:
        return self.update_many_outcome(
            {ChannelCollectionModel.Token.key: token, ChannelCollectionModel.Platform.key: platform},
            {"$set": {ChannelCollectionModel.DefaultName.key: new_default_name}})


ChannelManager = _ChannelManager()
ChannelCollectionManager = _ChannelCollectionManager()
