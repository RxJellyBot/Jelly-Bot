from typing import Optional

from bson import ObjectId
from pymongo import ReturnDocument

from extutils.checker import DecoParamCaster
from flags import Platform
from models import ChannelModel, ChannelConfigModel, OID_KEY
from mongodb.factory.results import (
    InsertOutcome, GetOutcome, OperationOutcome,
    ChannelRegistrationResult, ChannelGetResult, ChannelChangeNameResult
)

from ._base import BaseCollection

DB_NAME = "channel"


class ChannelManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "dict"
    model_class = ChannelModel

    def __init__(self):
        super().__init__(self.CACHE_KEY_SPEC1)
        self.create_index([(ChannelModel.Platform.key, 1), (ChannelModel.Token.key, 1)],
                          name="Channel Identity", unique=True)

    @DecoParamCaster({1: Platform, 2: str, 3: str})
    def register(self, platform: Platform, token: str, name: Optional[str] = "") -> ChannelRegistrationResult:
        entry, outcome, ex, insert_result = self.insert_one_data(
            ChannelModel, Platform=platform, Token=token, Name=name, Config=ChannelConfigModel.generate_default())

        if InsertOutcome.is_inserted(outcome):
            self.set_cache(self.CACHE_KEY_SPEC1, (platform, token), entry)
        elif InsertOutcome.data_found(outcome):
            entry = self.get_channel_token(platform, token)

        return ChannelRegistrationResult(outcome, entry, ex)

    @DecoParamCaster({1: ObjectId, 2: ObjectId, 3: str})
    def change_channel_name(self, channel_oid: ObjectId, root_oid: ObjectId, new_name: str) -> ChannelChangeNameResult:
        ex = None
        ret = self.find_one_and_update(
            {ChannelModel.Id.key: channel_oid},
            {"$set": {f"{ChannelModel.Name.key}.{root_oid}": new_name}},
            return_document=ReturnDocument.AFTER)

        try:
            if ret:
                outcome = OperationOutcome.O_COMPLETED
                self.set_cache(
                    self.CACHE_KEY_SPEC1,
                    (ret[ChannelModel.Platform.key], ret[ChannelModel.Token.key]),
                    ret, parse_cls=ChannelModel)
            else:
                outcome = OperationOutcome.X_CHANNEL_NOT_FOUND
        except Exception as e:
            outcome = OperationOutcome.X_ERROR
            ex = e

        return ChannelChangeNameResult(outcome, ret, ex)

    @DecoParamCaster({1: Platform, 2: str})
    def get_channel_token(self, platform: Platform, token: str) -> Optional[ChannelModel]:
        return self.get_cache(self.CACHE_KEY_SPEC1, (platform, token), parse_cls=ChannelModel,
                              acquire_args=({ChannelModel.Token.key: token, ChannelModel.Platform.key: platform},))

    @DecoParamCaster({1: ObjectId})
    def get_channel_oid(self, channel_oid: ObjectId) -> Optional[ChannelModel]:
        return self.get_cache_condition(
            self.CACHE_KEY_SPEC1, lambda item: item.id == channel_oid, parse_cls=ChannelModel,
            acquire_args=({ChannelModel.Id.key: channel_oid},), item_key_of_data=OID_KEY)

    # noinspection PyArgumentList
    @DecoParamCaster({1: Platform, 2: str})
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

        filter_ = {ChannelModel.Id.key: channel_oid}

        found_any = self.update_one(
            filter_,
            {"$set": {f"{ChannelModel.Config.key}.{json_key}": config_value}}).matched_count > 0

        if found_any:
            model = ChannelModel(**self.find_one(filter_), from_db=True)

            self.set_cache(self.CACHE_KEY_SPEC1, (model.platform, model.token), model, parse_cls=ChannelModel)

        return found_any


_inst = ChannelManager()
