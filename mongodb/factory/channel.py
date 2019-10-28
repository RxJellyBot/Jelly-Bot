from typing import Optional

from bson import ObjectId
from pymongo import ReturnDocument

from extutils.checker import param_type_ensure
from flags import Platform, ChannelType
from models import ChannelModel, ChannelConfigModel
from mongodb.factory.results import (
    WriteOutcome, GetOutcome, OperationOutcome,
    ChannelRegistrationResult, ChannelGetResult, ChannelChangeNameResult
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
        entry, outcome, ex, insert_result = self.insert_one_data(
            ChannelModel, Platform=platform, Token=token,
            Config=ChannelConfigModel.generate_default(DefaultName=default_name))

        if WriteOutcome.data_found(outcome):
            entry = self.get_channel_token(platform, token)

        return ChannelRegistrationResult(outcome, entry, ex)

    @param_type_ensure
    def change_channel_name(self, channel_oid: ObjectId, root_oid: ObjectId, new_name: str) -> ChannelChangeNameResult:
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
    def get_channel_oid(self, channel_oid: ObjectId) -> Optional[ChannelModel]:
        return self.find_one_casted({ChannelModel.Id.key: channel_oid}, parse_cls=ChannelModel)

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


_inst = ChannelManager()
