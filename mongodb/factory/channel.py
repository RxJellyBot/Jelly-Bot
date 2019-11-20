from typing import Optional

from bson import ObjectId
from pymongo import ReturnDocument

from extutils.checker import param_type_ensure
from flags import Platform
from models import ChannelModel, ChannelConfigModel, ChannelCollectionModel
from mongodb.utils import CursorWithCount
from mongodb.factory.results import (
    WriteOutcome, GetOutcome, OperationOutcome,
    ChannelRegistrationResult, ChannelGetResult, ChannelChangeNameResult, ChannelCollectionRegistrationResult
)

from ._base import BaseCollection

DB_NAME = "channel"


class ChannelManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "dict"
    model_class = ChannelModel

    def __init__(self):
        super().__init__()
        self.create_index(
            [(ChannelModel.Platform.key, 1), (ChannelModel.Token.key, 1)], name="Channel Identity", unique=True)

    @param_type_ensure
    def register(self, platform: Platform, token: str, default_name: str = None) -> ChannelRegistrationResult:
        entry, outcome, ex = self.insert_one_data(
            Platform=platform, Token=token,
            Config=ChannelConfigModel.generate_default(DefaultName=default_name))

        if outcome.data_found:
            entry = self.get_channel_token(platform, token)

        return ChannelRegistrationResult(outcome, entry, ex)

    @param_type_ensure
    def deregister(self, platform: Platform, token: str) -> WriteOutcome:
        return self.mark_accessibility(platform, token, False)

    @param_type_ensure
    def mark_accessibility(self, platform: Platform, token: str, accessibility: bool) -> WriteOutcome:
        return self.update_one_outcome(
            {ChannelModel.Platform.key: platform, ChannelModel.Token.key: token},
            {"$set": {ChannelModel.BotAccessible.key: accessibility}}
        )

    @param_type_ensure
    def update_channel_default_name(self, platform: Platform, token: str, default_name: str):
        return self.update_one_outcome(
            {ChannelModel.Platform.key: platform, ChannelModel.Token.key: token},
            {"$set": {f"{ChannelModel.Config.key}.{ChannelConfigModel.DefaultName.key}": default_name}}
        )

    @param_type_ensure
    def update_channel_nickname(self, channel_oid: ObjectId, root_oid: ObjectId, new_name: str) \
            -> ChannelChangeNameResult:
        """
        Update the channel name for the user. If `new_name` is falsy, then the user-specific name will be removed.
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
                ret = self.cast_model(ret, parse_cls=ChannelModel)
            else:
                outcome = OperationOutcome.X_CHANNEL_NOT_FOUND
        except Exception as e:
            outcome = OperationOutcome.X_ERROR
            ex = e

        return ChannelChangeNameResult(outcome, ret, ex)

    @param_type_ensure
    def get_channel_token(self, platform: Platform, token: str, auto_register: bool = False, default_name: str = None) \
            -> Optional[ChannelModel]:
        ret = self.find_one_casted(
            {ChannelModel.Token.key: token, ChannelModel.Platform.key: platform}, parse_cls=ChannelModel)

        if not ret and auto_register:
            reg_result = self.register(platform, token, default_name=default_name)
            if reg_result.success:
                ret = reg_result.model
            else:
                raise ValueError(
                    f"Channel registration failed in ChannelManager.get_channel_token. "
                    f"Platform: {platform} / Token: {token}")

        return ret

    @param_type_ensure
    def get_channel_oid(self, channel_oid: ObjectId, hide_private: bool = False) -> Optional[ChannelModel]:
        filter_ = {ChannelModel.Id.key: channel_oid}

        if hide_private:
            filter_[f"{ChannelModel.Config.key}.{ChannelConfigModel.InfoPrivate.key}"] = False

        return self.find_one_casted(filter_, parse_cls=ChannelModel)

    @param_type_ensure
    def get_channel_default_name(self, default_name: str, hide_private: bool = True) -> CursorWithCount:
        filter_ = \
            {f"{ChannelModel.Config.key}.{ChannelConfigModel.DefaultName.key}":
                    {"$regex": default_name, "$options": "i"}}

        if hide_private:
            filter_[f"{ChannelModel.Config.key}.{ChannelConfigModel.InfoPrivate.key}"] = False

        return self.find_cursor_with_count(filter_, parse_cls=ChannelModel)

    # noinspection PyArgumentList
    @param_type_ensure
    def get_channel_packed(self, platform: Platform, token: str) -> ChannelGetResult:
        if not isinstance(platform, Platform):
            platform = Platform(platform)

        model = self.get_channel_token(platform, token)

        if model is not None:
            outcome = GetOutcome.O_CACHE_DB
        else:
            outcome = GetOutcome.X_NOT_FOUND_ABORTED_INSERT

        return ChannelGetResult(outcome, model)

    def set_config(self, channel_oid: ObjectId, json_key, config_value) -> bool:
        if json_key not in ChannelConfigModel.model_json():
            raise ValueError(f"Attempt to set value to non-existing field in `ChannelModel`. ({json_key})")

        return self.update_one(
            {ChannelModel.Id.key: channel_oid},
            {"$set": {f"{ChannelModel.Config.key}.{json_key}": config_value}}).matched_count > 0


class ChannelCollectionManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "collection"
    model_class = ChannelCollectionModel

    def __init__(self):
        super().__init__()
        self.create_index(
            [(ChannelCollectionModel.Platform.key, 1), (ChannelCollectionModel.Token.key, 1)],
            name="Channel Collection Identity", unique=True)
        self.create_index(ChannelCollectionModel.ChildChannelOids.key, name="Child Channel Index")

    @param_type_ensure
    def register(
            self, platform: Platform, token: str, child_channel_oid: ObjectId, default_name: Optional[str] = None) \
            -> ChannelCollectionRegistrationResult:
        if not default_name:
            default_name = f"{token} ({platform.key})"

        entry, outcome, ex = self.insert_one_data(
            DefaultName=default_name, Platform=platform, Token=token, ChildChannelOids=[child_channel_oid])

        if outcome.data_found:
            entry = self.get_chcoll(platform, token)
            self.append_child_channel(entry.id, child_channel_oid)

        return ChannelCollectionRegistrationResult(outcome, entry, ex)

    @param_type_ensure
    def get_chcoll(self, platform: Platform, token: str) -> Optional[ChannelCollectionModel]:
        return self.find_one_casted(
            {ChannelCollectionModel.Token.key: token, ChannelCollectionModel.Platform.key: platform},
            parse_cls=ChannelCollectionModel)

    @param_type_ensure
    def get_chcoll_oid(self, chcoll_oid: ObjectId) -> Optional[ChannelCollectionModel]:
        return self.find_one_casted(
            {ChannelCollectionModel.Id.key: chcoll_oid},
            parse_cls=ChannelCollectionModel
        )

    @param_type_ensure
    def get_chcoll_child_channel(self, child_channel_oid: ObjectId):
        return self.find_one_casted(
            {ChannelCollectionModel.ChildChannelOids.key: child_channel_oid},
            parse_cls=ChannelCollectionModel
        )

    @param_type_ensure
    def append_child_channel(self, parent_oid: ObjectId, channel_oid: ObjectId) -> WriteOutcome:
        return self.update_one_outcome(
            {ChannelCollectionModel.Id.key: parent_oid},
            {"$addToSet": {ChannelCollectionModel.ChildChannelOids.key: channel_oid}})

    @param_type_ensure
    def update_default_name(self, platform: Platform, token: str, new_default_name: str):
        return self.update_one_outcome(
            {ChannelCollectionModel.Token.key: token, ChannelCollectionModel.Platform.key: platform},
            {"$set": {ChannelCollectionModel.DefaultName.key: new_default_name}})


_inst = ChannelManager()
_inst2 = ChannelCollectionManager()
